import requests

BASE_URL = "https://world.openfoodfacts.org"
USER_AGENT = "TrueLabel - Student Portfolio Project - contact@example.com"

def search_by_name(product_name: str, page_size: int = 5):
    """Search Open Food Facts by product name. Returns raw JSON response."""
    url = f"{BASE_URL}/cgi/search.pl"
    params = {
        "search_terms": product_name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": page_size,
    }
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()

def get_by_barcode(barcode: str):
    """Look up a single product by exact barcode. Returns raw JSON response."""
    url = f"{BASE_URL}/api/v2/product/{barcode}.json"
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()
