# neos_core/schemas/__init__.py
"""
Importación centralizada de todos los schemas
"""

# Tenant
from .tenant_schema import Tenant, TenantCreate, TenantOnboardingCreate, TenantOnboardingResponse

# User
from .user_schema import User, UserCreate, UserUpdate

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

# Cash Count
from .cash_count_schema import CashCountCreate, CashCountResponse
# Expense
from .expense_schema import ExpenseResponse, ExpenseSuggestionRequest, ExpenseSuggestionResponse

__all__ = [
    # Tenant
    "Tenant",
    "TenantCreate",
    "TenantOnboardingCreate",
    "TenantOnboardingResponse",
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
    "ClientUpdate",
    # Sales
    "SaleCreate",
    "SaleItemCreate",
    "SaleItemResponse",
    "SaleResponse",
    "SaleListResponse",
    "SaleFilters",
    # Cash Count
    "CashCountCreate",
    "CashCountResponse",
    # Expense
    "ExpenseResponse",
    "ExpenseSuggestionRequest",
    "ExpenseSuggestionResponse",
]
