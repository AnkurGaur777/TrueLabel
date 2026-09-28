from app.nlp.ingredient_flagger import flag_ingredients
from app.services.health_score import calculate_health_score

def _to_number(value):
    """Turn an OCR string like '609.7' into a float, or None if it isn't a number."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def _checked(name, value, max_value, notes):
    """Return the value if it is plausible, otherwise 'not available'.
    Impossible values (e.g. 334g of carbs per 100g) are OCR errors such as a
    dropped decimal point, so they are rejected and reported instead of shown."""
    number = _to_number(value)
    if number is None:
        return "not available"
    if number > max_value:
        notes.append(
            f"OCR read {name} as {number:g} per 100g, which is not possible, so it was ignored (a decimal point was probably missed)."
        )
        return "not available"
    return number

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
    (numeric per-100g values, sodium converted from mg to g), rejecting
    physically impossible values. Notes about rejected values are returned
    in product['ocr_notes']."""
    notes = []

    sodium_mg = _checked("sodium (mg)", parsed.get("sodium_mg"), 40000, notes)
    sodium_g = round(sodium_mg / 1000, 3) if isinstance(sodium_mg, float) else "not available"

    product = {
        "product_name": "Scanned nutrition label",
        "brands": "",
        "categories": "",
        "nutriscore_grade": "not available",
        "ingredients_text": "not available",
        "allergens": [],
        "nutrition_per_100g": {
            "energy_kcal": _checked("energy (kcal)", parsed.get("energy_kcal"), 900, notes),
            "carbs_g": _checked("carbohydrates (g)", parsed.get("carbs_g"), 100, notes),
            "sugars_g": _checked("sugars (g)", parsed.get("total_sugars_g"), 100, notes),
            "protein_g": _checked("protein (g)", parsed.get("protein_g"), 100, notes),
            "fat_g": _checked("fat (g)", parsed.get("total_fat_g"), 100, notes),
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
    product["ocr_notes"] = notes
    return product
