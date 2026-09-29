import re
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.result_builder import enrich_raw_food
from app.classifier.produce_classifier import classify_produce
from app.services.usda_client import search_usda
from app.services.usda_parser import parse_usda_food
from app.services.result_builder import enrich_raw_food
from app.services.scan_logger import log_scan, log_search

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/webp"}
MAX_FILE_SIZE_MB = 10

def _contains_whole_word(text: str, word: str) -> bool:
    """True if 'word' appears as a whole word, not inside a larger word
    ("apple" matches "Apples, raw" but not "Rose-apples, raw")."""
    return re.search(rf"\b{re.escape(word)}", text) is not None

def _pick_best_usda_match(foods: list, label: str):
    """Prefer 'Label..., raw', then any whole-word match containing 'raw',
    then the first result."""
    label_lower = label.lower()
    for food in foods:
        description = food.get("description", "").lower()
        if description.startswith(label_lower) and "raw" in description:
            return food
    for food in foods:
        description = food.get("description", "").lower()
        if _contains_whole_word(description, label_lower) and "raw" in description:
            return food
    return foods[0] if foods else None

@router.post("/classify")
async def classify_produce_photo(file: UploadFile = File(...)):
    """
    Identify a fruit/vegetable from a photo, look up its USDA nutrition, and
    return the standard product object plus the classifier's top guesses.
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
        predictions = classify_produce(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

    top_label = predictions[0]["label"]
    top_confidence = predictions[0]["confidence"]

    warnings = []
    if top_confidence < 0.6:
        warnings.append(
            f"The model is only {round(top_confidence * 100)}% sure this is {top_label}. Check the other guesses."
        )

    product = None
    try:
        usda_raw = search_usda(top_label, page_size=25)
        foods = usda_raw.get("foods", [])
        best_match = _pick_best_usda_match(foods, top_label)
        if best_match:
            nutrition_result = parse_usda_food(best_match)
            nutrition_result = enrich_raw_food(nutrition_result)
            product = nutrition_result
        else:
            warnings.append(f"No USDA nutrition entry found for '{top_label}'.")
    except Exception as e:
        warnings.append(f"Nutrition lookup failed: {e}")

    warnings.append(
        "Identification is AI-generated and may be wrong, especially for unusual angles or lighting. Nutrition is a USDA generic estimate, not specific to your exact item."
    )

    if product:
        log_search(file.filename, "produce_photo", product)
    else:
        log_scan(input_type="produce_photo", query_text=file.filename, product_name=top_label)

    return {
        "input_type": "produce_photo",
        "source": "usda_fdc",
        "product": product,
        "identification": {
            "best_guess": {"label": top_label, "confidence": top_confidence},
            "predictions": predictions,
        },
        "warnings": warnings,
    }
