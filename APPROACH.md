# Approach Note — Marksheet Extractor API

## 1. Extraction Approach

The extraction pipeline works in three stages:

**Stage 1 — File Ingestion**
Uploaded files are validated for type (JPG, PNG, PDF) and size (max 10MB).PDF files are converted page by page into PNG images using PyMuPDF at 200 DPI which is high enough for clear text recognition without excessive memory usage.Images are encoded to base64 for transmission to the Gemini API.

**Stage 2 — LLM Extraction**
The base64 image is sent to Google Gemini 2.5 Flash along with a carefully
engineered prompt. The prompt instructs Gemini to:
- Act as an expert marksheet data extractor
- Return a strictly structured JSON with predefined fields
- Assign a confidence score to every field based on explicit rules
- Return null with 0.0 confidence for missing fields

Gemini reads the marksheet visually (as a vision-language model) and fills in the JSON structure. This approach generalizes across different marksheet formats, boards, and universities without any hardcoded rules.

**Stage 3 — Parsing and Validation**
The raw LLM response is cleaned (markdown code blocks stripped if present)and parsed as JSON. Pydantic schemas validate the structure before returning to the client, ensuring a consistent output format every time.

## 2. Model Selection — Why Gemini 2.5 Flash?

- Vision capability: Gemini 2.5 Flash is a multimodal model that can read and understand text within images natively — essential for marksheet extraction.
- Speed: Flash variants are optimized for low latency, making API responses fast.
- Free tier availability: Gemini 2.5 Flash is available on Google AI Studio's free tier, making it accessible without billing for development and testing.
- Accuracy: In testing across multiple marksheet formats (CBSE, state boards, universities), Gemini 2.5 Flash consistently extracted fields with high accuracy.

## 3. Confidence Scoring

Confidence scores are derived through **prompt-based calibration**. The LLM is explicitly instructed to score each field using these rules:


- 0.95 – 1.0 - Clearly visible, unambiguous text 
- 0.75 – 0.94 - Mostly clear but slightly uncertain 
- 0.50 – 0.74 - Partially visible or inferred from context 
- 0.25 – 0.49 - Guessed from context, hard to read 
- 0.00 – 0.24 - Not found or completely unreadable 

This approach leverages the LLM's internal uncertainty about what it reads in the image. Fields that are clearly printed get high scores, fields that are absent, blurry, or ambiguous get lower scores. This makes confidence scores meaningful and interpretable rather than arbitrary.

## 4. Design Choices

- **FastAPI** was chosen for its async support (handles concurrent requests natively), automatic Swagger UI generation, and Pydantic integration.
- **Pydantic schemas** enforce a consistent JSON structure regardless of what the LLM returns — preventing malformed responses from reaching the client.
- **JWT authentication** secures all extraction endpoints with stateless tokens that expire after 60 minutes.
- **PyMuPDF** converts PDFs to images server-side so the same vision-based extraction pipeline works for both images and PDFs uniformly.
- **Prompt engineering** is the core of extraction quality — the prompt defines the output schema, confidence rules, and fallback behavior for missing fields.

## 5. Limitations and Future Improvements

- Currently processes only the first page of multi-page PDFs
- Confidence scores are LLM-reported, not statistically calibrated
- A database layer could replace the hardcoded demo user for production use