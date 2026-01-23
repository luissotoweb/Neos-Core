from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from neos_core.database.config import Base


class ProductEmbedding(Base):
    __tablename__ = "product_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    model = Column(String(120), nullable=False)
    content_hash = Column(String(64), nullable=False)
    embedding = Column(JSONB, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    product = relationship("Product")
    tenant = relationship("Tenant")

    __table_args__ = (
        UniqueConstraint("tenant_id", "product_id", name="uq_product_embeddings_tenant_product"),
        {"schema": None},
    )
