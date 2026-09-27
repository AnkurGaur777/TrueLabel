import re
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.classifier.produce_classifier import classify_produce
from app.services.usda_client import search_usda
from app.services.usda_parser import parse_usda_food

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/webp"}
MAX_FILE_SIZE_MB = 10

def _contains_whole_word(text: str, word: str) -> bool:
    """Check if 'word' appears as a whole word in 'text', not as a substring
    of a larger word. E.g. "apple" should match "Apples, raw" but NOT match
    "Rose-apples, raw" (where "apple" is embedded inside "rose-apples")."""
    return re.search(rf"\b{re.escape(word)}", text) is not None

def _pick_best_usda_match(foods: list, label: str):
    """
    Prefer, in order:
    1. A description that STARTS WITH the label (word-boundary) AND contains "raw"
       (e.g. "Apples, raw" for label "apple")
    2. A description that contains the label as a whole word AND "raw"
    3. Fall back to the first result if nothing matches "raw" at all
    """
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
    Accept a photo of raw produce, identify it using an image classifier,
    then look up its nutrition data from USDA FoodData Central, preferring
    the raw/unprocessed version of that food.
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

    nutrition_result = None
    nutrition_error = None
    try:
        usda_raw = search_usda(top_label, page_size=25)
        foods = usda_raw.get("foods", [])
        best_match = _pick_best_usda_match(foods, top_label)
        if best_match:
            nutrition_result = parse_usda_food(best_match)
    except Exception as e:
        nutrition_error = str(e)

    return {
        "filename": file.filename,
        "predictions": predictions,
        "best_guess": {
            "label": top_label,
            "confidence": top_confidence,
        },
        "nutrition": nutrition_result,
        "nutrition_error": nutrition_error,
        "note": "Identification is AI-generated and may be wrong, especially for unusual angles or lighting. Nutrition data is a USDA generic estimate for this food, not specific to your exact item.",
    }
