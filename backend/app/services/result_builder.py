from app.nlp.ingredient_flagger import flag_ingredients
from app.services.health_score import calculate_health_score

def _to_number(value):
    """Turn an OCR string like '609.7' into a float. Anything else
    ('not detected') becomes 'not available'."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return "not available"

def enrich_raw_food(food: dict) -> dict:
    """Give a USDA raw/generic food the same fields a packaged product has,
    so the frontend can render every result with one component."""
    food["ingredient_flags"] = flag_ingredients(food.get("ingredients_text", ""))
    food["health_score"] = calculate_health_score(food)
    food["alternatives"] = {
        "can_search": False,
        "reason": "Healthier alternatives are only available for packaged products.",
        "alternatives": [],
    }
    return food

def ocr_to_product(parsed: dict) -> dict:
    """Convert the OCR parser's string output into the standard product shape
    (numeric values in per-100g units, sodium converted from mg to g)."""
    sodium_mg = _to_number(parsed.get("sodium_mg"))
    sodium_g = round(sodium_mg / 1000, 3) if isinstance(sodium_mg, float) else "not available"

    product = {
        "product_name": "Scanned nutrition label",
        "brands": "",
        "categories": "",
        "nutriscore_grade": "not available",
        "ingredients_text": "not available",
        "allergens": [],
        "nutrition_per_100g": {
            "energy_kcal": _to_number(parsed.get("energy_kcal")),
            "carbs_g": _to_number(parsed.get("carbs_g")),
            "sugars_g": _to_number(parsed.get("total_sugars_g")),
            "protein_g": _to_number(parsed.get("protein_g")),
            "fat_g": _to_number(parsed.get("total_fat_g")),
            "sodium_g": sodium_g,
        },
    }
    product["ingredient_flags"] = flag_ingredients("")
    product["health_score"] = calculate_health_score(product)
    product["alternatives"] = {
        "can_search": False,
        "reason": "Alternatives are not available for scanned labels (no category information).",
        "alternatives": [],
    }
    return product
