"""HTTP routers, one module per resource."""

from necktie.routers.category import router as category_router
from necktie.routers.district import router as district_router
from necktie.routers.doctor import router as doctor_router

__all__ = ["category_router", "district_router", "doctor_router"]
