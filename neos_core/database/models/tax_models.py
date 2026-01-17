# neos_core/database/models/tax_models.py
"""
Modelos de datos fiscales (tablas maestras globales)
IMPORTANTE: PointOfSale y Currency están en archivos separados
"""
from sqlalchemy import Column, Integer, String
from neos_core.database.config import Base


class TaxIdType(Base):
    """Tipos de identificación fiscal (CUIT, DNI, RUC, etc.)"""
    __tablename__ = "tax_id_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # Ej: "CUIT", "DNI"

    def __repr__(self):
        return f"<TaxIdType(id={self.id}, name={self.name})>"


class TaxResponsibility(Base):
    """Responsabilidades fiscales (IVA RI, Monotributo, etc.)"""
    __tablename__ = "tax_responsibilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # Ej: "Responsable Inscripto"

    def __repr__(self):
        return f"<TaxResponsibility(id={self.id}, name={self.name})>"