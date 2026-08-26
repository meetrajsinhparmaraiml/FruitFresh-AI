from fastapi import FastAPI

app = FastAPI(
    title="FruitFresh AI",
    description="Real-time fruit freshness analysis API",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return the health status of the API."""
    return {"status": "ok"}