"""FastAPI application entry point."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from necktie.cache.lifespan import lifespan
from necktie.routers import category_router, district_router, doctor_router

app = FastAPI(title="necktie", version="0.1.0", lifespan=lifespan)

# Comma-separated allowed origins, e.g. CORS_ORIGINS="https://a.com,https://b.com".
# Defaults to "*" for local development (prototype file:// page).
cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(doctor_router)
app.include_router(category_router)
app.include_router(district_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}
