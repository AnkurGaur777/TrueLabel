from fastapi import APIRouter, HTTPException
from app.services.openfoodfacts_client import search_by_name, get_by_barcode
from app.services.product_parser import parse_product
from app.services.usda_client import search_usda
from app.services.usda_parser import parse_usda_food

router = APIRouter()

@router.get("/search")
def search_product(query: str, is_barcode: bool = False):
    """
    Search for a product by name, or look it up by barcode.
    Set is_barcode=true when the query is a barcode number.

    Barcode searches only check Open Food Facts (packaged products have barcodes,
    raw produce does not).

    Name searches query BOTH Open Food Facts (packaged products) and USDA
    FoodData Central (raw/generic foods like fruits and vegetables) at the same
    time, and return both sets of results separately labeled. This is because a
    plain name like "banana" is genuinely ambiguous -- it could mean packaged
    banana chips/yogurt/etc, or a raw banana -- so we show both rather than
    guessing which one the user meant.

    If one source fails (down, timeout, etc.), we still return results from the
    other source rather than failing the whole request.
    """
    if is_barcode:
        try:
            raw = get_by_barcode(query)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Error contacting Open Food Facts: {str(e)}")

        if raw.get("status") != 1:
            raise HTTPException(status_code=404, detail="Product not found for this barcode")
        product = raw.get("product", {})
        return {"source": "openfoodfacts", "result": parse_product(product)}

    off_results = []
    off_error = None
    try:
        raw = search_by_name(query)
        off_results = [parse_product(p) for p in raw.get("products", [])]
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
