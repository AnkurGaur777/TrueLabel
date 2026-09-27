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
            "energy_kcal": nutriments.get("energy-kcal_100g", "not available"),
            "carbs_g": nutriments.get("carbohydrates_100g", "not available"),
            "sugars_g": nutriments.get("sugars_100g", "not available"),
            "protein_g": nutriments.get("proteins_100g", "not available"),
            "fat_g": nutriments.get("fat_100g", "not available"),
            "sodium_g": nutriments.get("sodium_100g", "not available"),
        },
    }
