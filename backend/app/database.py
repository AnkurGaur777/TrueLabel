from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def init_db():
    """Create tables if they don't exist yet."""
    from app.models import scan_log  # noqa: F401 (importing registers the table)
    Base.metadata.create_all(bind=engine)
