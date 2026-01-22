# neos_core/schemas/__init__.py
"""
Importación centralizada de todos los schemas
"""

# Tenant
from .tenant_schema import Tenant, TenantCreate, TenantOnboardingCreate, TenantOnboardingResponse

# User
from .user_schema import User, UserCreate

# Role
from .role_schema import Role

# Auth/Token
from .token_schema import Token, TokenData

# Products
from .product_schema import (
    ProductType,
    Product, 
    ProductCreate, 
    ProductUpdate, 
    ProductListResponse,
    ProductKitComponent,
    ProductKitComponentCreate
)

# Config (Currency, POS)
from .config_schema import (
    Currency, 
    CurrencyCreate,
    PointOfSale, 
    PointOfSaleCreate,
    PointOfSaleUpdate
)

# Client
from .client_schema import Client, ClientCreate

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
    "TenantOnboardingCreate",
    "TenantOnboardingResponse",
    # User
    "User",
    "UserCreate",
    # Role
    "Role",
    # Auth
    "Token",
    "TokenData",
    # Product
    "Product",
    "ProductType",
    "ProductCreate",
    "ProductUpdate",
    "ProductListResponse",
    "ProductKitComponent",
    "ProductKitComponentCreate",
    # Config
    "Currency",
    "CurrencyCreate",
    "PointOfSale",
    "PointOfSaleCreate",
    "PointOfSaleUpdate",
    # Client
    "Client",
    "ClientCreate",
    # Sales
    "SaleCreate",
    "SaleItemCreate",
    "SaleItemResponse",
    "SaleResponse",
    "SaleListResponse",
    "SaleFilters",
]
