# neos_core/database/models/inventory_model.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from neos_core.database.config import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, index=True)  # Código de barras o SKU
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, default=0.0)
    stock = Column(Integer, default=0)

    # El "ancla" al Tenant para el aislamiento
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    # Relación
    tenant = relationship("Tenant")