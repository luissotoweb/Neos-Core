from enum import Enum

from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, Text, DateTime, JSON, Enum as SqlEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from neos_core.database.config import Base


class ProductType(str, Enum):
    stock = "stock"
    service = "service"
    kit = "kit"


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

    purchase_unit = Column(String(50), nullable=False, default="unit")
    sale_unit = Column(String(50), nullable=False, default="unit")
    conversion_factor = Column(Numeric(10, 4), nullable=False, default=1)

    stock = Column(Numeric(10, 4), nullable=False, default=0)
    min_stock = Column(Numeric(10, 4), nullable=True)

    tax_rate = Column(Numeric(5, 2), nullable=False, default=0)

    attributes = Column(JSONB, nullable=True)

    product_type = Column(SqlEnum(ProductType, name="product_type"), nullable=False, default=ProductType.stock)
    is_active = Column(Boolean, default=True, nullable=False)
    is_service = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    tenant = relationship("Tenant")
    kit_components = relationship(
        "ProductKit",
        foreign_keys="ProductKit.kit_product_id",
        cascade="all, delete-orphan",
        back_populates="kit_product"
    )

    __table_args__ = ({'schema': None},)


class ProductKit(Base):
    __tablename__ = "product_kits"

    id = Column(Integer, primary_key=True, index=True)
    kit_product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    component_product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Numeric(10, 4), nullable=False, default=0)

    kit_product = relationship(
        "Product",
        foreign_keys=[kit_product_id],
        back_populates="kit_components"
    )
    component_product = relationship(
        "Product",
        foreign_keys=[component_product_id]
    )

    __table_args__ = ({'schema': None},)
