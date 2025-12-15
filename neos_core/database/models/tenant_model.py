# neos_core/database/models/tenant_model.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from neos_core.database.config import Base  # Importamos la base


# --- MODELO TENANT (CLIENTE) ---
class Tenant(Base):
    """
    Representa a un cliente o inquilino principal en la arquitectura multi-tenant.
    Cada tenant tiene su propio conjunto de datos lógicamente separados.
    """
    __tablename__ = "tenants"

    # Campos de Datos
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False, doc="Nombre único del cliente o inquilino.")
    description = Column(Text, nullable=True, doc="Descripción detallada del cliente o su rubro.")
    is_active = Column(Boolean, default=True, doc="Indica si el tenant está activo y puede acceder al sistema.")

    # Campos de Seguimiento
    created_at = Column(DateTime(timezone=True), server_default=func.now(),
                        doc="Fecha y hora de creación del registro.")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(),
                        doc="Última fecha y hora de actualización del registro.")

    # Relación (Usamos una cadena para referenciar a 'User' que aún no está importado)
    users = relationship("User", back_populates="tenant", lazy="dynamic")