from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from neos_core.database.config import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)

    sku = Column(String(100), nullable=False, index=True)
    barcode = Column(String(100), nullable=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    cost = Column(Numeric(10, 2), nullable=False, default=0)
    price = Column(Numeric(10, 2), nullable=False)

    stock = Column(Numeric(10, 4), nullable=False, default=0)
    min_stock = Column(Numeric(10, 4), nullable=True)

    tax_rate = Column(Numeric(5, 2), nullable=False, default=0)

    # IMPORTANTE: Solo JSON, sin JSONB
    attributes = Column(JSON, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)
    is_service = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    tenant = relationship("Tenant")

    __table_args__ = ({'schema': None},)