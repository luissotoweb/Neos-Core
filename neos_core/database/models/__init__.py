# neos_core/database/models/__init__.py

# Forzamos la importación de las clases para que Base.metadata.create_all()
# sepa de su existencia.

from .tenant_model import Tenant
from .user_model import User
from .role_model import Role