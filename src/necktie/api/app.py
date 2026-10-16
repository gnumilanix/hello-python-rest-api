"""FastAPI application."""

from fastapi import FastAPI

from necktie.api.doctors import router as doctors_router

app = FastAPI(title="necktie", version="0.1.0")
app.include_router(doctors_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}
