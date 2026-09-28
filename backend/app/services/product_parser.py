def _round(value, digits=1):
    """Round real numbers for clean display; leave text like 'not available' alone."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return round(value, digits)
    return value

def parse_product(raw_product: dict) -> dict:
    """Extract clean, consistent fields from a raw Open Food Facts product object."""
    nutriments = raw_product.get("nutriments", {})

    return {
        "product_name": raw_product.get("product_name") or "Unknown product",
        "brands": raw_product.get("brands", ""),
        "categories": raw_product.get("categories", ""),
        "nutriscore_grade": raw_product.get("nutriscore_grade", "not available"),
        "ingredients_text": raw_product.get("ingredients_text", "not available"),
        "allergens": raw_product.get("allergens_tags", []),
        "nutrition_per_100g": {
            "energy_kcal": _round(nutriments.get("energy-kcal_100g", "not available")),
            "carbs_g": _round(nutriments.get("carbohydrates_100g", "not available")),
            "sugars_g": _round(nutriments.get("sugars_100g", "not available")),
            "protein_g": _round(nutriments.get("proteins_100g", "not available")),
            "fat_g": _round(nutriments.get("fat_100g", "not available")),
            "sodium_g": _round(nutriments.get("sodium_100g", "not available"), 3),
        },
    }
