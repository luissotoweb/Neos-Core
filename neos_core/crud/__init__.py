# neos_core/crud/__init__.py
"""
Importación centralizada de todas las operaciones CRUD
"""

# Tenant CRUD
from .tenant_crud import (
    get_tenant_by_name,
    get_tenant_by_id,
    create_tenant,
    get_tenants
)

# User CRUD
from .user_crud import (
    get_user_by_email,
    get_user_by_id,
    get_users,
    get_users_by_tenant,
    create_user,
    verify_password,
    get_password_hash,
    get_visible_users
)

# Product CRUD (renombrado de inventory)
from .product_crud import (
    create_product,
    get_products_by_tenant,
    get_product_by_id,
    get_product_by_sku,
    get_product_by_barcode,
    update_product,
    delete_product,
    get_low_stock_products
)

# Config CRUD (Currency y PointOfSale)
from .config_crud import (
    # Currency
    get_currencies,
    get_currency_by_id,
    get_currency_by_code,
    create_currency,
    # PointOfSale
    get_pos_by_tenant,
    get_pos_by_id,
    get_pos_by_code,
    create_pos,
    update_pos,
    delete_pos
)

# Client CRUD
from .client_crud import (
    create_client,
    get_clients_by_tenant,
    get_client_by_tax_id
)

# Sales CRUD
from .sales_crud import (
    create_sale,
    get_sale_by_id,
    get_sales,
    cancel_sale,
    pause_sale,
    resume_sale
)

# Cash Count CRUD
from .cash_count_crud import (
    create_cash_count,
    get_cash_count
)

# AI CRUD
from .ai_crud import (
    create_ai_interaction,
)

# Expense CRUD
from .expense_crud import (
    create_expense,
    get_expense_by_id,
    get_expenses,
)

# Purchase CRUD
from .purchase_crud import (
    create_purchase,
    get_purchase_by_id,
    get_purchases,
)

__all__ = [
    # Tenant
    "get_tenant_by_name",
    "get_tenant_by_id",
    "create_tenant",
    "get_tenants",
    # User
    "get_user_by_email",
    "get_user_by_id",
    "get_users",
    "get_users_by_tenant",
    "create_user",
    "verify_password",
    "get_password_hash",
    "get_visible_users",
    # Product
    "create_product",
    "get_products_by_tenant",
    "get_product_by_id",
    "get_product_by_sku",
    "get_product_by_barcode",
    "update_product",
    "delete_product",
    "get_low_stock_products",
    # Config
    "get_currencies",
    "get_currency_by_id",
    "get_currency_by_code",
    "create_currency",
    "get_pos_by_tenant",
    "get_pos_by_id",
    "get_pos_by_code",
    "create_pos",
    "update_pos",
    "delete_pos",
    # Client
    "create_client",
    "get_clients_by_tenant",
    "get_client_by_tax_id",
    # Sales
    "create_sale",
    "get_sale_by_id",
    "get_sales",
    "cancel_sale",
    # AI
    "create_ai_interaction",
    "pause_sale",
    "resume_sale",
    # Cash Count
    "create_cash_count",
    "get_cash_count",
    # Expense
    "create_expense",
    "get_expense_by_id",
    "get_expenses",
    # Purchase
    "create_purchase",
    "get_purchase_by_id",
    "get_purchases",
]
