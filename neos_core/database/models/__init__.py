# neos_core/database/models/__init__.py
from .user_model import User
from .role_model import Role
from .tenant_model import Tenant
from .inventory_model import Product
from .tax_models import TaxIdType, TaxResponsibility, Currency, PointOfSale
from .client_model import Client  # Importar Client
from .sales_model import Sale, SaleDetail  # Importar Sale después de Client