"""HTTP routers, one module per resource."""

from necktie.routers.doctor import router as doctor_router

__all__ = ["doctor_router"]
