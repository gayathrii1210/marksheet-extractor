from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.config import settings
from app.services.file_service import validate_and_read_file
from app.services.llm_service import extract_from_images
from app.models.schemas import ExtractionResponse

router = APIRouter()
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Checks if the JWT token in the request is valid.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("/extract", response_model=ExtractionResponse)
async def extract_marksheet(
    file: UploadFile = File(...),
    username: str = Depends(verify_token)
):
    """
    Main endpoint:
    1. Verifies JWT token
    2. Validates and reads the uploaded file
    3. Sends to Gemini for extraction
    4. Returns structured JSON
    """
    try:
        base64_images = await validate_and_read_file(file)
        extracted_data = await extract_from_images(base64_images)
        return extracted_data
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/extract/batch", response_model=list[ExtractionResponse])
async def extract_batch(
    files: list[UploadFile] = File(...),
    username: str = Depends(verify_token)
):
    """
    Bonus batch endpoint — accepts multiple marksheets at once.
    """
    results = []
    for file in files:
        try:
            base64_images = await validate_and_read_file(file)
            extracted_data = await extract_from_images(base64_images)
            results.append(extracted_data)
        except Exception as e:
            results.append({"error": str(e), "filename": file.filename})
    return results