import re

def _find_nutrient_value(text: str, patterns: list) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return "not detected"

def _normalize_text(raw_text: str) -> str:
    text = raw_text.replace("\n", " ")
    text = re.sub(r"(\d),(\d)", r"\1.\2", text)
    return text

def parse_nutrition_from_text(raw_text: str) -> dict:
    text = _normalize_text(raw_text)

    energy = _find_nutrient_value(text, [
        r"energy[^\d]*(\d+\.?\d*)\s*k?cal",
        r"(\d+\.?\d*)\s*kcal",
    ])

    protein = _find_nutrient_value(text, [
        r"protein[^\d]*(\d+\.\d+)",
        r"protein[^\d]*(\d+)",
    ])

    carbs = _find_nutrient_value(text, [
        r"carbohydrates?[^\d]*(\d+\.\d+)",
        r"carbohydrates?[^\d]*(\d+)",
    ])

    total_sugars = _find_nutrient_value(text, [
        r"total sugars?[^\d]*(\d+\.\d+)",
        r"total sugars?[^\d]*(\d+)",
    ])

    added_sugars = _find_nutrient_value(text, [
        r"added sugars?[^\d]*(\d+\.\d+)",
        r"added sugars?[^\d]*(\d+)",
    ])

    total_fat = _find_nutrient_value(text, [
        r"total fat[^\d]*(\d+\.\d+)",
        r"total fat[^\d]*(\d+)",
    ])

    saturated_fat = _find_nutrient_value(text, [
        r"s.turated\s*fat[^\d]*(\d+\.\d+)",
        r"s.turated\s*fat[^\d]*(\d+)",
        r"sat[a-z]*\s*fat[^\d]*(\d+\.\d+)",
        r"sat[a-z]*\s*fat[^\d]*(\d+)",
    ])

    trans_fat = _find_nutrient_value(text, [
        r"trans\s*fat[^\d]*(\d+\.\d+)",
        r"trans\s*fat[^\d]*(\d+)",
    ])

    sodium = _find_nutrient_value(text, [
        r"sodium[^\d]*(\d+\.\d+)",
        r"sodium[^\d]*(\d+)",
    ])

    return {
        "energy_kcal": energy,
        "protein_g": protein,
        "carbs_g": carbs,
        "total_sugars_g": total_sugars,
        "added_sugars_g": added_sugars,
        "total_fat_g": total_fat,
        "saturated_fat_g": saturated_fat,
        "trans_fat_g": trans_fat,
        "sodium_mg": sodium,
        "note": "Values extracted from photo via OCR -- may contain errors, especially decimal points and units. Verify against the physical label if accuracy matters.",
    }
