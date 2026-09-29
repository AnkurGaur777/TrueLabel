from fastapi import APIRouter, UploadFile, File, HTTPException
from app.ocr.extractor import extract_text_from_image
from app.ocr.nutrition_parser import parse_nutrition_from_text
from app.services.result_builder import ocr_to_product
from app.services.scan_logger import log_scan

router = APIRouter()
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/webp"}
MAX_FILE_SIZE_MB = 10

@router.post("/scan")
async def scan_label(file: UploadFile = File(...)):
    """
    Accept an uploaded photo of a nutrition label, run OCR, and return a full
    product object (nutrition, health score) in the same shape /search uses,
    plus the raw OCR text for transparency.
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
            "input_type": "label_photo",
            "source": "ocr",
            "product": None,
            "raw_text": "",
            "warnings": ["No text could be detected in this image. Try a clearer, well-lit, flat-on photo of the label."],
        }

    parsed = parse_nutrition_from_text(raw_text)
    product = ocr_to_product(parsed)
    warnings = product.pop("ocr_notes", [])
    log_scan(input_type="label_photo", query_text=file.filename, nutrition_data=parsed)

    return {
        "input_type": "label_photo",
        "source": "ocr",
        "product": product,
        "raw_text": raw_text,
        "warnings": warnings,
    }