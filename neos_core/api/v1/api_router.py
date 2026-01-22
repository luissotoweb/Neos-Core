# neos_core/api/v1/api_router.py
"""
Router principal que agrupa todos los endpoints de la API v1
"""
from fastapi import APIRouter

# Importar todos los routers de endpoints
from neos_core.api.v1.endpoints import (
    tenant_routes,
    user_routes,
    product_routes,  # Renombrado de inventory_routes
    config_routes,
    client_routes,
    sales_routes,  # ⭐ NUEVO
    analytics_routes,
    ai_routes,
    cash_count_routes,
    accounting_routes,
)

# Crear router principal
api_router = APIRouter()

# ===== INCLUIR ROUTERS CON PREFIJOS Y TAGS =====

# Tenants
api_router.include_router(
    tenant_routes.router,
    prefix="/tenants",
    tags=["Tenants"]
)

# Users
api_router.include_router(
    user_routes.router,
    prefix="/users",
    tags=["Users"]
)

# Products (Inventory)
api_router.include_router(
    product_routes.router,
    prefix="/products",
    tags=["Products"]
)

# Configuration (Currencies & PointOfSale)
api_router.include_router(
    config_routes.router,
    prefix="/config",
    tags=["Configuration"]
)

# Clients
api_router.include_router(
    client_routes.router,
    prefix="/clients",
    tags=["Clients"]
)

# ⭐ Sales (NUEVO)
api_router.include_router(
    sales_routes.router,
    # Ya tiene prefix="/sales" interno
    tags=["Sales"]
)

# 📊 Analytics
api_router.include_router(
    analytics_routes.router,
    tags=["Analytics"]
)

# 🤖 AI
api_router.include_router(
    ai_routes.router,
    tags=["AI"]
)
# Cash Counts
api_router.include_router(
    cash_count_routes.router,
    tags=["Cash Counts"]
)
# Accounting
api_router.include_router(
    accounting_routes.router,
    tags=["Accounting"]
)
