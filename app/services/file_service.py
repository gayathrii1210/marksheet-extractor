import fitz  # PyMuPDF
import base64
from fastapi import UploadFile, HTTPException
import io
from PIL import Image

ALLOWED_TYPES = ["image/jpeg", "image/png", "application/pdf"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

async def validate_and_read_file(file: UploadFile) -> list:
    """
    Validates file type and size.
    Returns a list of base64-encoded images (one per page for PDF).
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}'. Only JPG, PNG, PDF allowed."
        )

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 10 MB."
        )

    if file.content_type == "application/pdf":
        return extract_images_from_pdf(contents)
    else:
        return [encode_image_bytes(contents)]


def extract_images_from_pdf(pdf_bytes: bytes) -> list:
    """Converts each PDF page to a base64 image."""
    images = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page in doc:
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")
        images.append(encode_image_bytes(img_bytes))
    return images


def encode_image_bytes(img_bytes: bytes) -> str:
    """Returns base64-encoded string of image bytes."""
    return base64.b64encode(img_bytes).decode("utf-8")