from fastapi import APIRouter, UploadFile, File, HTTPException
from app.ocr.extractor import extract_text_from_image

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/webp"}
MAX_FILE_SIZE_MB = 10

@router.post("/scan")
async def scan_label(file: UploadFile = File(...)):
    """
    Accept an uploaded photo of a nutrition label, run OCR on it, and return
    the raw extracted text. This is step 1 of OCR -- parsing this raw text
    into structured nutrition data comes in a later step.
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {ALLOWED_CONTENT_TYPES}",
        )

    image_bytes = await file.read()

    size_mb = len(image_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large: {size_mb:.1f}MB. Max allowed: {MAX_FILE_SIZE_MB}MB",
        )

    try:
        raw_text = extract_text_from_image(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

    if not raw_text.strip():
        return {
            "filename": file.filename,
            "raw_text": "",
            "warning": "No text could be detected in this image. Try a clearer, well-lit photo of the label.",
        }

    return {
        "filename": file.filename,
        "raw_text": raw_text,
    }
