"""FastAPI application entry point."""

from fastapi import FastAPI

from necktie.routers import doctor_router

app = FastAPI(title="necktie", version="0.1.0")
app.include_router(doctor_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}
