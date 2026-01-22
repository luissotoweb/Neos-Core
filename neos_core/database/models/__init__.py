# neos_core/database/models/__init__.py
"""
Importación centralizada de todos los modelos.
IMPORTANTE: Importar todos los modelos aquí para que SQLAlchemy los registre.
"""

# Modelos base
from neos_core.database.models.tenant_model import Tenant
from neos_core.database.models.user_model import User
from neos_core.database.models.role_model import Role

# Modelos de configuración fiscal (solo fiscales, sin Currency ni POS)
from neos_core.database.models.tax_models import TaxIdType, TaxResponsibility

# Modelos de inventario
from neos_core.database.models.product_model import Product, ProductKit, ProductType

# Modelos de clientes
from neos_core.database.models.client_model import Client

# Modelos de configuración (importar de archivos separados)
from neos_core.database.models.currency_model import Currency
from neos_core.database.models.point_of_sale import PointOfSale

# Modelos de onboarding
from neos_core.database.models.tenant_onboarding_model import OnboardingPreset, TenantOnboardingConfig

# Modelos de ventas
from neos_core.database.models.sales_model import Sale, SaleDetail

# Modelos contables
from neos_core.database.models.accounting_model import AccountingMove, AccountingLine

# Exportar todos
__all__ = [
    # Base
    "Tenant",
    "User",
    "Role",
    # Fiscal
    "TaxIdType",
    "TaxResponsibility",
    # Inventario
    "Product",
    "ProductKit",
    "ProductType",
    # Clientes
    "Client",
    # Configuración
    "Currency",
    "PointOfSale",
    # Ventas
    "Sale",
    "SaleDetail",
    # Contabilidad
    "AccountingMove",
    "AccountingLine",
    # Onboarding
    "OnboardingPreset",
    "TenantOnboardingConfig",
]
