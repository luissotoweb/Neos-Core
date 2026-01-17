# neos_core/database/models/tenant_model.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from neos_core.database.config import Base


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

    # --- Identidad Fiscal ---
    tax_id = Column(String, unique=True, index=True, nullable=True)  # El CUIT/RUT/NIT
    tax_id_type_id = Column(Integer, ForeignKey("tax_id_types.id"), nullable=True)
    tax_responsibility_id = Column(Integer, ForeignKey("tax_responsibilities.id"), nullable=True)

    # --- Configuración de Facturación Electrónica ---
    electronic_invoicing_enabled = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Habilita/deshabilita la facturación electrónica (CAE). Por defecto: deshabilitada."
    )
    electronic_invoicing_provider = Column(
        String(50),
        nullable=True,
        doc="Proveedor de facturación: AFIP (Argentina), SAT (México), SII (Chile), etc."
    )

    # Campos de Seguimiento
    created_at = Column(DateTime(timezone=True), server_default=func.now(),
                        doc="Fecha y hora de creación del registro.")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(),
                        doc="Última fecha y hora de actualización del registro.")

    # Relaciones
    users = relationship("User", back_populates="tenant", lazy="dynamic")
    tax_type = relationship("TaxIdType")
    responsibility = relationship("TaxResponsibility")