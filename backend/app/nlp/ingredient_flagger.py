from langdetect import detect, LangDetectException
from app.nlp.flag_config import (
    ALLERGEN_KEYWORDS,
    ARTIFICIAL_ADDITIVE_KEYWORDS,
    HIGH_SUGAR_INDICATORS,
    ULTRA_PROCESSED_MARKERS,
)

def _find_matches(text: str, keyword_list: list) -> list:
    text_lower = text.lower()
    return [kw for kw in keyword_list if kw in text_lower]

def _find_allergens(text: str) -> list:
    text_lower = text.lower()
    found = []
    for allergen_name, keywords in ALLERGEN_KEYWORDS.items():
        matched_keywords = [kw for kw in keywords if kw in text_lower]
        if matched_keywords:
            found.append({
                "allergen": allergen_name,
                "matched_terms": matched_keywords,
            })
    return found

def _detect_language(text: str):
    try:
        return detect(text)
    except LangDetectException:
        return None

def flag_ingredients(ingredients_text: str) -> dict:
    """
    Analyze an ingredients list and flag potential concerns. Keyword lists
    include common French, German, and Spanish equivalents for key terms
    (sugar, milk, wheat, etc), since Open Food Facts frequently returns
    non-English ingredient text and this avoids depending on an unreliable
    free translation API. Language is detected and reported for transparency,
    but matching runs directly against the multilingual keyword lists.
    """
    if not ingredients_text or ingredients_text.strip().lower() in ("not available", "not applicable (raw/generic food)", ""):
        return {
            "can_analyze": False,
            "reason": "No ingredients text available for this product.",
            "allergens": [],
            "artificial_additives": [],
            "high_sugar_indicators": [],
            "ultra_processed_markers": [],
            "summary": "Ingredient analysis not available.",
            "detected_language": None,
        }

    detected_language = _detect_language(ingredients_text)

    allergens = _find_allergens(ingredients_text)
    additives = _find_matches(ingredients_text, ARTIFICIAL_ADDITIVE_KEYWORDS)
    sugar_indicators = _find_matches(ingredients_text, HIGH_SUGAR_INDICATORS)
    processed_markers = _find_matches(ingredients_text, ULTRA_PROCESSED_MARKERS)

    summary_parts = []
    if allergens:
        allergen_names = ", ".join(a["allergen"].replace("_", " ") for a in allergens)
        summary_parts.append(f"Contains or may contain common allergens: {allergen_names}")
    if additives:
        summary_parts.append(f"Contains {len(additives)} artificial additive(s)")
    if sugar_indicators:
        summary_parts.append(f"Contains {len(sugar_indicators)} sugar-related ingredient(s)")
    if processed_markers:
        summary_parts.append(f"Shows {len(processed_markers)} ultra-processed marker(s)")

    summary = ". ".join(summary_parts) if summary_parts else "No major concerns flagged based on available keyword matching."

    return {
        "can_analyze": True,
        "allergens": allergens,
        "artificial_additives": additives,
        "high_sugar_indicators": sugar_indicators,
        "ultra_processed_markers": processed_markers,
        "summary": summary,
        "detected_language": detected_language,
    }
