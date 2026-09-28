from app.database import SessionLocal
from app.models.scan_log import ScanLog

def log_scan(input_type, query_text=None, product_name=None, nutrition_data=None,
             flags=None, health_score=None, alternatives_shown=None):
    """Write one row to scan_logs. Never raises: if MySQL is down or the write
    fails, the API request still succeeds and only the logging is skipped."""
    try:
        with SessionLocal() as session:
            session.add(ScanLog(
                input_type=input_type,
                query_text=(query_text or None) and str(query_text)[:255],
                product_name=(product_name or None) and str(product_name)[:255],
                nutrition_data=nutrition_data,
                flags=flags,
                health_score=health_score if isinstance(health_score, int) else None,
                alternatives_shown=alternatives_shown,
            ))
            session.commit()
    except Exception as e:
        print(f"WARNING: could not log scan: {e}")

def log_search(query, input_type, product):
    """Log a search/barcode result using the top parsed product."""
    log_scan(
        input_type=input_type,
        query_text=query,
        product_name=product.get("product_name"),
        nutrition_data=product.get("nutrition_per_100g"),
        flags=product.get("ingredient_flags"),
        health_score=(product.get("health_score") or {}).get("score"),
        alternatives_shown=product.get("alternatives"),
    )
