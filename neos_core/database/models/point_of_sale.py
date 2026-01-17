# neos_core/database/models/point_of_sale_model.py
"""
Modelo de Punto de Venta (POS) / Caja / Sucursal
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from neos_core.database.config import Base


class PointOfSale(Base):
    """
    Representa un punto de venta, caja o sucursal.
    Cada tenant puede tener múltiples puntos de venta.
    """
    __tablename__ = "points_of_sale"

    # IDs
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)

    # Datos del POS
    name = Column(String(100), nullable=False)  # Ej: "Caja 1", "Sucursal Centro"
    code = Column(String(20), nullable=False)  # Ej: "POS-001" (para numeración de facturas)
    location = Column(String(200), nullable=True)  # Dirección física

    # Estado
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    # Relaciones
    tenant = relationship("Tenant")

    def __repr__(self):
        return f"<PointOfSale(id={self.id}, name={self.name}, code={self.code})>"