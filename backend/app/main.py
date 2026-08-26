from fastapi import FastAPI
from app.db.database import init_db
from app.api.v1.endpoints.scans import router as scans_router

app = FastAPI(title="FruitFresh AI", version="2.0.0")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(scans_router)

@app.get("/health")
def health():
    return {"status": "ok"}
