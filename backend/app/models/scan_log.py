from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from app.database import Base

class ScanLog(Base):
    """One row per search/scan/classify request."""
    __tablename__ = "scan_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    input_type = Column(String(20), nullable=False)  # search, barcode, label_photo, produce_photo
    query_text = Column(String(255), nullable=True)
    product_name = Column(String(255), nullable=True)
    nutrition_data = Column(JSON, nullable=True)
    flags = Column(JSON, nullable=True)
    health_score = Column(Integer, nullable=True)
    alternatives_shown = Column(JSON, nullable=True)
