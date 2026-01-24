from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from neos_core.database.config import Base


class TenantCategory(Base):
    __tablename__ = "tenant_categories"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_tenant_categories_tenant_name"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant")


class TenantActiveModule(Base):
    __tablename__ = "tenant_active_modules"
    __table_args__ = (
        UniqueConstraint("tenant_id", "module_key", name="uq_tenant_modules_tenant_key"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    module_key = Column(String(120), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant")
