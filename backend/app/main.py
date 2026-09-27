from fastapi import FastAPI
from app.api.search import router as search_router
from app.api.scan import router as scan_router
from app.api.classify import router as classify_router

app = FastAPI(title="TrueLabel API")

app.include_router(search_router)
app.include_router(scan_router)
app.include_router(classify_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "TrueLabel API"}
