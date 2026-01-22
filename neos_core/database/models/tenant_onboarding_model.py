from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from neos_core.database.config import Base


class OnboardingPreset(Base):
    __tablename__ = "onboarding_presets"

    id = Column(Integer, primary_key=True, index=True)
    rubro = Column(String(100), unique=True, index=True, nullable=False)
    categories = Column(JSON, nullable=False)
    active_modules = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant_configs = relationship("TenantOnboardingConfig", back_populates="preset")


class TenantOnboardingConfig(Base):
    __tablename__ = "tenant_onboarding_configs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), unique=True, nullable=False, index=True)
    preset_id = Column(Integer, ForeignKey("onboarding_presets.id"), nullable=True)
    rubro = Column(String(100), nullable=False)
    categories = Column(JSON, nullable=False)
    active_modules = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant")
    preset = relationship("OnboardingPreset", back_populates="tenant_configs")
