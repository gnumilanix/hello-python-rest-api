"""FastAPI application entry point."""

from fastapi import FastAPI

from necktie.cache import lifespan
from necktie.routers import category_router, district_router, doctor_router

app = FastAPI(title="necktie", version="0.1.0", lifespan=lifespan)
app.include_router(doctor_router)
app.include_router(category_router)
app.include_router(district_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}
