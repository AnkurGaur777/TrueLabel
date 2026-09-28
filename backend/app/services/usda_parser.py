def _get_nutrient(food: dict, nutrient_name: str, unit: str = None):
    """Find a specific nutrient value from USDA's foodNutrients list by name.
    If unit is given (e.g. "KCAL", "MG"), only entries with that unit match --
    needed because USDA lists some nutrients (like energy) in multiple units."""
    for nutrient in food.get("foodNutrients", []):
        name = nutrient.get("nutrientName", "")
        if nutrient_name.lower() in name.lower():
            if unit and nutrient.get("unitName", "").upper() != unit.upper():
                continue
            return nutrient.get("value", "not available")
    return "not available"

def _mg_to_g(value):
    """USDA reports sodium in mg; Open Food Facts uses grams. Convert so both
    sources use the same unit."""
    if isinstance(value, (int, float)):
        return round(value / 1000, 4)
    return value

def _get_first_nutrient(food: dict, names: list, unit: str = None):
    """Try several possible USDA names for the same nutrient, in order."""
    for name in names:
        value = _get_nutrient(food, name, unit)
        if value != "not available":
            return value
    return "not available"

def parse_usda_food(food: dict) -> dict:
    """Extract clean, consistent fields from a raw USDA FoodData Central food
    object. Matches the same output shape and units as parse_product() for
    Open Food Facts, so the frontend and health score can treat both
    sources identically."""
    return {
        "product_name": food.get("description", "Unknown food"),
        "brands": "",
        "categories": food.get("foodCategory", "Raw/generic food"),
        "nutriscore_grade": "not applicable",
        "ingredients_text": "not applicable (raw/generic food)",
        "allergens": [],
        "nutrition_per_100g": {
            "energy_kcal": _get_nutrient(food, "Energy", unit="KCAL"),
            "carbs_g": _get_nutrient(food, "Carbohydrate, by difference"),
            "sugars_g": _get_first_nutrient(food, ["Sugars, total", "Total Sugars", "Sugars, Total"]),
            "protein_g": _get_nutrient(food, "Protein"),
            "fat_g": _get_nutrient(food, "Total lipid (fat)"),
            "sodium_g": _mg_to_g(_get_nutrient(food, "Sodium", unit="MG")),
        },
    }
