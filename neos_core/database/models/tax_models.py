from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from neos_core.database.config import Base

# --- TABLAS MAESTRAS (Globales para todos) ---

class TaxIdType(Base):
    __tablename__ = "tax_id_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False) # Ej: "CUIT", "DNI"

class TaxResponsibility(Base):
    __tablename__ = "tax_responsibilities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False) # Ej: "Responsable Inscripto"

class Currency(Base):
    __tablename__ = "currencies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False) # Ej: "Peso Argentino"
    code = Column(String, unique=True, nullable=False) # Ej: "ARS", "USD"
    symbol = Column(String, nullable=False) # Ej: "$"

# --- CONFIGURACIÓN POR TENANT (Privadas por empresa) ---

class PointOfSale(Base):
    __tablename__ = "points_of_sale"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    number = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    tenant = relationship("Tenant")