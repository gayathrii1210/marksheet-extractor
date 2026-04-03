from google import genai
from google.genai import types
import json
import re
from app.config import settings

# Initialize the new Gemini client
client = genai.Client(api_key=settings.GEMINI_API_KEY)


def build_prompt() -> str:
    return """
    You are an expert marksheet data extractor. 
    Analyze the provided marksheet image carefully and extract all information.

    Return ONLY a valid JSON object with this exact structure (no extra text, no markdown):
    {
        "candidate_details": {
            "name": {"value": "...", "confidence": 0.0},
            "father_name": {"value": "...", "confidence": 0.0},
            "mother_name": {"value": "...", "confidence": 0.0},
            "roll_no": {"value": "...", "confidence": 0.0},
            "registration_no": {"value": "...", "confidence": 0.0},
            "dob": {"value": "...", "confidence": 0.0},
            "exam_year": {"value": "...", "confidence": 0.0},
            "board_or_university": {"value": "...", "confidence": 0.0},
            "institution": {"value": "...", "confidence": 0.0}
        },
        "subjects": [
            {
                "subject": {"value": "...", "confidence": 0.0},
                "max_marks": {"value": "...", "confidence": 0.0},
                "obtained_marks": {"value": "...", "confidence": 0.0},
                "grade": {"value": "...", "confidence": 0.0}
            }
        ],
        "overall_result": {
            "result": {"value": "PASS/FAIL", "confidence": 0.0},
            "total_marks": {"value": "...", "confidence": 0.0},
            "percentage": {"value": "...", "confidence": 0.0},
            "division": {"value": "...", "confidence": 0.0},
            "grade": {"value": "...", "confidence": 0.0}
        },
        "issue_info": {
            "issue_date": {"value": "...", "confidence": 0.0},
            "issue_place": {"value": "...", "confidence": 0.0}
        }
    }

    Confidence score rules:
    - 0.95 to 1.0 → clearly visible, unambiguous text
    - 0.75 to 0.94 → mostly clear but slightly uncertain
    - 0.50 to 0.74 → partially visible or inferred
    - 0.25 to 0.49 → guessed from context, hard to read
    - 0.0 to 0.24 → not found or completely unreadable

    If a field is not present, set value to null and confidence to 0.0.
    Return ONLY the JSON. No explanation. No markdown. No code blocks.
    """


def parse_llm_response(response_text: str) -> dict:
    cleaned = re.sub(r"```(?:json)?", "", response_text).strip()
    cleaned = cleaned.strip("`").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned invalid JSON: {e}\nRaw response: {response_text}")


async def extract_from_images(base64_images: list) -> dict:
    image_data = base64_images[0]

    # Convert base64 string to bytes
    import base64
    image_bytes = base64.b64decode(image_data)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/png"
                    ),
                    types.Part.from_text(text=build_prompt())
                ]
            )
        ]
    )

    raw_text = response.text
    parsed = parse_llm_response(raw_text)
    return parsed