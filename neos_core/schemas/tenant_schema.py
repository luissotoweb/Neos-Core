from pydantic import BaseModel
from typing import Optional, List

class TenantBase(BaseModel):
    name: str
    description: Optional[str] = None
    tax_id: Optional[str] = None
    tax_id_type_id: Optional[int] = None
    tax_responsibility_id: Optional[int] = None

class TenantCreate(TenantBase):
    pass


class TenantOnboardingCreate(BaseModel):
    rubro: str
    name: str
    description: Optional[str] = None
    tax_id: Optional[str] = None
    tax_id_type_id: Optional[int] = None
    tax_responsibility_id: Optional[int] = None


class TenantOnboardingConfig(BaseModel):
    rubro: str
    categories: List[str]
    active_modules: List[str]

class Tenant(TenantBase):
    id: int
    is_active: bool
    class Config:
        from_attributes = True


class TenantOnboardingResponse(BaseModel):
    tenant: Tenant
    onboarding: TenantOnboardingConfig
