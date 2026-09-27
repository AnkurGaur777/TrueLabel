import requests
from app.config import USDA_FDC_API_KEY

BASE_URL = "https://api.nal.usda.gov/fdc/v1"

def search_usda(query: str, page_size: int = 5):
    """Search USDA FoodData Central for raw/generic foods. Returns raw JSON response."""
    url = f"{BASE_URL}/foods/search"
    params = {
        "query": query,
        "pageSize": page_size,
        "api_key": USDA_FDC_API_KEY,
        "dataType": ["Foundation", "SR Legacy"],
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()
