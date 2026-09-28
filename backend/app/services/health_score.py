def _num(value):
    """Return the value if it is a real number, otherwise None (missing data)."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    return None

def calculate_health_score(product: dict) -> dict:
    """
    Rules-based health score from 0-100 (higher = healthier), estimated from
    per-100g nutrition data plus ingredient flags when available.

    Starts at 100, then deducts/adds points per rule. Rules whose input data
    is missing are SKIPPED (never treated as zero), and the result reports
    which nutrients were actually used. If fewer than 3 of the 5 core
    nutrients are available, no score is given rather than guessing.

    Thresholds are loosely modeled on UK FSA traffic-light levels per 100g.
    This is an approximate estimate, not an official health rating.
    """
    n = product.get("nutrition_per_100g", {}) or {}
    sugars = _num(n.get("sugars_g"))
    sodium = _num(n.get("sodium_g"))
    fat = _num(n.get("fat_g"))
    energy = _num(n.get("energy_kcal"))
    protein = _num(n.get("protein_g"))

    available = {
        "sugars": sugars, "sodium": sodium, "fat": fat,
        "energy": energy, "protein": protein,
    }
    data_used = [k for k, v in available.items() if v is not None]
    missing = [k for k, v in available.items() if v is None]

    if len(data_used) < 3:
        return {
            "can_score": False,
            "reason": "Not enough nutrition data to estimate a score.",
            "score": None,
            "rating": None,
            "breakdown": [],
            "data_used": data_used,
            "disclaimer": "Estimated score only, not an official health rating.",
        }

    breakdown = []

    def add(points, reason):
        breakdown.append({"points": points, "reason": reason})

    if sugars is not None:
        if sugars > 22.5:
            add(-30, f"High sugar ({sugars}g per 100g)")
        elif sugars > 5:
            add(-10, f"Moderate sugar ({sugars}g per 100g)")

    if sodium is not None:
        if sodium > 0.6:
            add(-20, f"High sodium ({sodium}g per 100g)")
        elif sodium > 0.12:
            add(-8, f"Moderate sodium ({sodium}g per 100g)")

    if fat is not None:
        if fat > 17.5:
            add(-15, f"High fat ({fat}g per 100g)")
        elif fat > 3:
            add(-5, f"Moderate fat ({fat}g per 100g)")

    if energy is not None:
        if energy > 400:
            add(-10, f"Very energy-dense ({energy} kcal per 100g)")
        elif energy > 250:
            add(-4, f"Energy-dense ({energy} kcal per 100g)")

    if protein is not None:
        if protein >= 10:
            add(8, f"High protein ({protein}g per 100g)")
        elif protein >= 5:
            add(3, f"Good protein ({protein}g per 100g)")

    flags = product.get("ingredient_flags") or {}
    if flags.get("can_analyze"):
        additive_count = len(flags.get("artificial_additives", []))
        if additive_count:
            add(-min(additive_count * 5, 15), f"{additive_count} artificial additive(s)")
        processed_count = len(flags.get("ultra_processed_markers", []))
        if processed_count:
            add(-min(processed_count * 3, 9), f"{processed_count} ultra-processed marker(s)")

    score = 100 + sum(item["points"] for item in breakdown)
    score = max(0, min(100, score))

    if score >= 70:
        rating = "green"
    elif score >= 50:
        rating = "yellow"
    else:
        rating = "red"

    return {
        "can_score": True,
        "score": score,
        "rating": rating,
        "breakdown": breakdown,
        "data_used": data_used,
        "missing_nutrients": missing,
        "confidence": "low" if "sugars" in missing else ("high" if not missing else "medium"),
        "disclaimer": "Estimated score only, not an official health rating.",
    }
