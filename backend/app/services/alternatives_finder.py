import requests

BASE_URL = "https://world.openfoodfacts.org"
USER_AGENT = "TrueLabel - Student Portfolio Project - contact@example.com"

NUTRISCORE_RANK = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "not-applicable": 99, "unknown": 99}

# A candidate must have at least this much LESS sugar to count as "lower sugar",
# so trivial differences (35g vs 36g) are not presented as healthier alternatives.
MIN_SUGAR_IMPROVEMENT = 0.20

def _nutriscore_rank(grade: str) -> int:
    return NUTRISCORE_RANK.get((grade or "").lower(), 99)

def _search_by_category(category_tag: str, page_size: int = 20):
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
    """Use the first category tag as the category to search within."""
    if not categories_text:
        return ""
    return categories_text.split(",")[0].strip()

def find_healthier_alternatives(product: dict, max_results: int = 5) -> dict:
    """
    Find products in the same category with a better Nutri-Score or clearly
    lower sugar (at least 20% lower). Candidates are collected first, then
    ranked (best Nutri-Score first, then lowest sugar), so the top results
    are the strongest ones. Returns a clear "none found" result rather than
    forcing a weak match.
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
        raw = _search_by_category(category)
    except Exception as e:
        return {
            "can_search": False,
            "reason": f"Error searching for alternatives: {str(e)}",
            "alternatives": [],
        }

    found = []
    for candidate in raw.get("products", []):
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
            and candidate_sugar <= original_sugar * (1 - MIN_SUGAR_IMPROVEMENT)
        )

        if not (is_better_grade or is_lower_sugar):
            continue

        reasons = []
        if is_better_grade:
            reasons.append(f"better Nutri-Score ({candidate_grade.upper()} vs {original_grade.upper()})")
        if is_lower_sugar:
            reasons.append(f"lower sugar ({round(candidate_sugar, 1)}g vs {original_sugar}g per 100g)")

        sort_sugar = candidate_sugar if isinstance(candidate_sugar, (int, float)) else 999
        found.append((candidate_rank, sort_sugar, {
            "product_name": candidate_name,
            "brands": candidate.get("brands", ""),
            "nutriscore_grade": candidate_grade,
            "sugars_g": round(candidate_sugar, 1) if isinstance(candidate_sugar, (int, float)) else "not available",
            "why_better": " and ".join(reasons),
        }))

    found.sort(key=lambda item: (item[0], item[1]))
    alternatives = [item[2] for item in found[:max_results]]

    if not alternatives:
        return {
            "can_search": True,
            "reason": "No clearly healthier alternatives found in this category.",
            "alternatives": [],
        }

    return {"can_search": True, "reason": None, "alternatives": alternatives}
