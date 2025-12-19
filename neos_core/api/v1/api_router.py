# neos_core/api/v1/api_router.py
from fastapi import APIRouter
from neos_core.api.v1.endpoints import user_routes, inventory_routes, tenant_routes

api_router = APIRouter()

api_router.include_router(tenant_routes.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(user_routes.router, prefix="/users", tags=["Users"])
api_router.include_router(inventory_routes.router, prefix="/products", tags=["Inventory"])