def _get_nutrient(food: dict, nutrient_name: str):
    """Find a specific nutrient value from USDA's foodNutrients list by name."""
    for nutrient in food.get("foodNutrients", []):
        name = nutrient.get("nutrientName", "")
        if nutrient_name.lower() in name.lower():
            return nutrient.get("value", "not available")
    return "not available"

def parse_usda_food(food: dict) -> dict:
    """Extract clean, consistent fields from a raw USDA FoodData Central food object.
    Matches the same output shape as parse_product() for Open Food Facts, so the
    frontend can treat both sources identically."""
    return {
        "product_name": food.get("description", "Unknown food"),
        "brands": "",
        "categories": food.get("foodCategory", "Raw/generic food"),
        "nutriscore_grade": "not applicable",
        "ingredients_text": "not applicable (raw/generic food)",
        "allergens": [],
        "nutrition_per_100g": {
            "energy_kcal": _get_nutrient(food, "Energy"),
            "carbs_g": _get_nutrient(food, "Carbohydrate, by difference"),
            "sugars_g": _get_nutrient(food, "Sugars, total"),
            "protein_g": _get_nutrient(food, "Protein"),
            "fat_g": _get_nutrient(food, "Total lipid (fat)"),
            "sodium_g": _get_nutrient(food, "Sodium"),
        },
    }
