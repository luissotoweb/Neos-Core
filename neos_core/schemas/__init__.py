# neos_core/schemas/__init__.py
"""
Importación centralizada de todos los schemas
"""

# Tenant
from .tenant_schema import Tenant, TenantCreate, TenantUpdate

# User
from .user_schema import User, UserCreate, UserUpdate

# Role
from .role_schema import Role

# Auth/Token
from .token_schema import Token, TokenData

# Products
from .product_schema import (
    Product, 
    ProductCreate, 
    ProductUpdate, 
    ProductListResponse
)

# Config (Currency, POS)
from .config_schema import (
    Currency, 
    CurrencyCreate,
    CurrencyUpdate,
    PointOfSale, 
    PointOfSaleCreate,
    PointOfSaleUpdate
)

# Client
from .client_schema import Client, ClientCreate, ClientUpdate

# Sales
from .sales_schema import (
    SaleCreate,
    SaleItemCreate, 
    SaleItemResponse, 
    SaleResponse,
    SaleListResponse,
    SaleFilters
)

__all__ = [
    # Tenant
    "Tenant",
    "TenantCreate",
    "TenantUpdate",
    # User
    "User",
    "UserCreate",
    "UserUpdate",
    # Role
    "Role",
    # Auth
    "Token",
    "TokenData",
    # Product
    "Product",
    "ProductCreate",
    "ProductUpdate",
    "ProductListResponse",
    # Config
    "Currency",
    "CurrencyCreate",
    "CurrencyUpdate",
    "PointOfSale",
    "PointOfSaleCreate",
    "PointOfSaleUpdate",
    # Client
    "Client",
    "ClientCreate",
    "ClientUpdate",
    # Sales
    "SaleCreate",
    "SaleItemCreate",
    "SaleItemResponse",
    "SaleResponse",
    "SaleListResponse",
    "SaleFilters",
]
