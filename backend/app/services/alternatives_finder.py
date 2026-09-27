import requests

BASE_URL = "https://world.openfoodfacts.org"
USER_AGENT = "TrueLabel - Student Portfolio Project - contact@example.com"

NUTRISCORE_RANK = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "not-applicable": 99, "unknown": 99}

def _nutriscore_rank(grade: str) -> int:
    return NUTRISCORE_RANK.get((grade or "").lower(), 99)

def _search_by_category(category_tag: str, page_size: int = 15):
    """Search Open Food Facts for products in a specific category."""
    url = f"{BASE_URL}/cgi/search.pl"
    params = {
        "tagtype_0": "categories",
        "tag_contains_0": "contains",
        "tag_0": category_tag,
        "json": 1,
        "page_size": page_size,
        "action": "process",
    }
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()

def _extract_primary_category(categories_text: str) -> str:
    """
    Open Food Facts' categories field is a comma-separated list, often mixing
    languages and specificity levels (e.g. "en:Biscuits, Cookies, Sucres").
    Take the first tag as a reasonable category to search within -- it's
    usually the most relevant/general one for that product.
    """
    if not categories_text:
        return ""
    first = categories_text.split(",")[0].strip()
    return first

def find_healthier_alternatives(product: dict, max_results: int = 5) -> dict:
    """
    Given a parsed product (with categories, nutriscore_grade, nutrition_per_100g,
    product_name), search for other products in the same category that have a
    better Nutri-Score or lower sugar content. Returns the alternatives found,
    or a clear "none found" result rather than forcing a weak match.
    """
    category = _extract_primary_category(product.get("categories", ""))
    if not category:
        return {
            "can_search": False,
            "reason": "No category information available for this product.",
            "alternatives": [],
        }

    original_name = product.get("product_name", "")
    original_grade = product.get("nutriscore_grade", "not-applicable")
    original_rank = _nutriscore_rank(original_grade)
    original_sugar = product.get("nutrition_per_100g", {}).get("sugars_g")

    try:
        raw = _search_by_category(category, page_size=15)
    except Exception as e:
        return {
            "can_search": False,
            "reason": f"Error searching for alternatives: {str(e)}",
            "alternatives": [],
        }

    candidates = raw.get("products", [])
    alternatives = []

    for candidate in candidates:
        candidate_name = candidate.get("product_name", "")
        if not candidate_name or candidate_name == original_name:
            continue

        candidate_grade = candidate.get("nutriscore_grade", "not-applicable")
        candidate_rank = _nutriscore_rank(candidate_grade)
        candidate_sugar = candidate.get("nutriments", {}).get("sugars_100g")

        is_better_grade = candidate_rank < original_rank
        is_lower_sugar = (
            isinstance(candidate_sugar, (int, float))
            and isinstance(original_sugar, (int, float))
            and candidate_sugar < original_sugar
        )

        if is_better_grade or is_lower_sugar:
            reason_parts = []
            if is_better_grade:
                reason_parts.append(f"better Nutri-Score ({candidate_grade.upper()} vs {original_grade.upper()})")
            if is_lower_sugar:
                reason_parts.append(f"lower sugar ({candidate_sugar}g vs {original_sugar}g per 100g)")

            alternatives.append({
                "product_name": candidate_name,
                "brands": candidate.get("brands", ""),
                "nutriscore_grade": candidate_grade,
                "sugars_g": candidate_sugar if candidate_sugar is not None else "not available",
                "why_better": " and ".join(reason_parts),
            })

        if len(alternatives) >= max_results:
            break

    if not alternatives:
        return {
            "can_search": True,
            "reason": "No clearly healthier alternatives found in this category.",
            "alternatives": [],
        }

    return {
        "can_search": True,
        "reason": None,
        "alternatives": alternatives,
    }
