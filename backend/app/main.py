from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.search import router as search_router
from app.api.scan import router as scan_router
from app.api.classify import router as classify_router
from app.api.logs import router as logs_router
from app.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # If MySQL is unreachable, the API still starts; logging is just skipped.
    try:
        init_db()
        print("Database ready: scan_logs table OK")
    except Exception as e:
        print(f"WARNING: database unavailable, scan logging disabled: {e}")
    yield

app = FastAPI(title="TrueLabel API", lifespan=lifespan)

app.include_router(search_router)
app.include_router(scan_router)
app.include_router(classify_router)
app.include_router(logs_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "TrueLabel API"}
