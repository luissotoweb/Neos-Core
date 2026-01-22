# neos_core/api/v1/endpoints/__init__.py
"""
Exporta todos los routers de endpoints para facilitar imports
"""
from . import (
    tenant_routes,
    user_routes,
    product_routes,
    config_routes,
    client_routes,
    sales_routes,
    cash_count_routes
)

__all__ = [
    "tenant_routes",
    "user_routes",
    "product_routes",
    "config_routes",
    "client_routes",
    "sales_routes",
    "cash_count_routes",
]
