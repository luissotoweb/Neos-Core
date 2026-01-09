# neos_core/api/v1/api_router.py
from fastapi import APIRouter
from neos_core.api.v1.endpoints import user_routes, inventory_routes, tenant_routes, config_routes
from neos_core.api.v1.endpoints import client_routes

api_router = APIRouter()

api_router.include_router(tenant_routes.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(user_routes.router, prefix="/users", tags=["Users"])
api_router.include_router(inventory_routes.router, prefix="/products", tags=["Inventory"])
api_router.include_router(config_routes.router, prefix="/config", tags=["Configuración"])
api_router.include_router(client_routes.router, prefix="/clients", tags=["Clientes"])