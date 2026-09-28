from fastapi import APIRouter, HTTPException
from app.services.openfoodfacts_client import search_by_name, get_by_barcode
from app.services.product_parser import parse_product
from app.services.usda_client import search_usda
from app.services.usda_parser import parse_usda_food
from app.nlp.ingredient_flagger import flag_ingredients
from app.services.alternatives_finder import find_healthier_alternatives
from app.services.health_score import calculate_health_score
from app.services.scan_logger import log_search

router = APIRouter()

def _enrich_product(product: dict) -> dict:
    """Add ingredient risk flags, a health score, and healthier alternatives
    to a parsed packaged product. Flags come first because the score uses them."""
    product["ingredient_flags"] = flag_ingredients(product.get("ingredients_text", ""))
    product["health_score"] = calculate_health_score(product)
    product["alternatives"] = find_healthier_alternatives(product)
    return product

def _enrich_raw_food(food: dict) -> dict:
    """Raw/generic foods have no ingredient list, so they only get a score."""
    food["health_score"] = calculate_health_score(food)
    return food

@router.get("/search")
def search_product(query: str, is_barcode: bool = False):
    """
    Search for a product by name, or look it up by barcode.
    Set is_barcode=true when the query is a barcode number.

    Barcode searches only check Open Food Facts.

    Name searches query BOTH Open Food Facts (packaged products) and USDA
    FoodData Central (raw/generic foods) and return both sets separately.

    Every result includes an estimated health_score. Packaged products also
    include ingredient_flags and healthier alternatives.
    """
    if is_barcode:
        try:
            raw = get_by_barcode(query)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Error contacting Open Food Facts: {str(e)}")

        if raw.get("status") != 1:
            raise HTTPException(status_code=404, detail="Product not found for this barcode")
        product = _enrich_product(parse_product(raw.get("product", {})))
        log_search(query, "barcode", product)
        return {"source": "openfoodfacts", "result": product}

    off_results = []
    off_error = None
    try:
        raw = search_by_name(query)
        off_results = [_enrich_product(parse_product(p)) for p in raw.get("products", [])]
    except Exception as e:
        off_error = str(e)

    usda_results = []
    usda_error = None
    try:
        usda_raw = search_usda(query)
        usda_results = [_enrich_raw_food(parse_usda_food(f)) for f in usda_raw.get("foods", [])]
    except Exception as e:
        usda_error = str(e)

    if not off_results and not usda_results:
        raise HTTPException(
            status_code=404,
            detail=f"No results from either source. Open Food Facts error: {off_error}. USDA error: {usda_error}",
        )

    top = off_results[0] if off_results else usda_results[0]
    log_search(query, "search", top)

    return {
        "packaged_products": {
            "source": "openfoodfacts",
            "results": off_results,
            "error": off_error,
        },
        "raw_generic_foods": {
            "source": "usda_fdc",
            "results": usda_results,
            "error": usda_error,
        },
    }
