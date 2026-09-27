from fastapi import APIRouter, HTTPException
from app.services.openfoodfacts_client import search_by_name, get_by_barcode
from app.services.product_parser import parse_product
from app.services.usda_client import search_usda
from app.services.usda_parser import parse_usda_food
from app.nlp.ingredient_flagger import flag_ingredients

router = APIRouter()

def _attach_flags(product: dict) -> dict:
    """Add ingredient risk flags to a parsed product dict, using its
    ingredients_text field. Returns the product with an added
    'ingredient_flags' key."""
    product["ingredient_flags"] = flag_ingredients(product.get("ingredients_text", ""))
    return product

@router.get("/search")
def search_product(query: str, is_barcode: bool = False):
    """
    Search for a product by name, or look it up by barcode.
    Set is_barcode=true when the query is a barcode number.

    Barcode searches only check Open Food Facts.

    Name searches query BOTH Open Food Facts (packaged products) and USDA
    FoodData Central (raw/generic foods) and return both sets separately.

    Every packaged product result includes ingredient_flags: allergens,
    artificial additives, high-sugar indicators, and ultra-processed markers
    detected from the ingredients text via keyword matching.
    """
    if is_barcode:
        try:
            raw = get_by_barcode(query)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Error contacting Open Food Facts: {str(e)}")

        if raw.get("status") != 1:
            raise HTTPException(status_code=404, detail="Product not found for this barcode")
        product = parse_product(raw.get("product", {}))
        product = _attach_flags(product)
        return {"source": "openfoodfacts", "result": product}

    off_results = []
    off_error = None
    try:
        raw = search_by_name(query)
        off_results = [_attach_flags(parse_product(p)) for p in raw.get("products", [])]
    except Exception as e:
        off_error = str(e)

    usda_results = []
    usda_error = None
    try:
        usda_raw = search_usda(query)
        usda_results = [parse_usda_food(f) for f in usda_raw.get("foods", [])]
    except Exception as e:
        usda_error = str(e)

    if not off_results and not usda_results:
        raise HTTPException(
            status_code=404,
            detail=f"No results from either source. Open Food Facts error: {off_error}. USDA error: {usda_error}",
        )

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
