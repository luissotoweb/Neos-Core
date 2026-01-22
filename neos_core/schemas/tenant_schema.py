from pydantic import BaseModel
from typing import Optional

class TenantBase(BaseModel):
    name: str
    description: Optional[str] = None
    tax_id: Optional[str] = None
    tax_id_type_id: Optional[int] = None
    tax_responsibility_id: Optional[int] = None

class TenantCreate(TenantBase):
    pass

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tax_id: Optional[str] = None
    tax_id_type_id: Optional[int] = None
    tax_responsibility_id: Optional[int] = None
    electronic_invoicing_enabled: Optional[bool] = None
    electronic_invoicing_provider: Optional[str] = None
    is_active: Optional[bool] = None

class Tenant(TenantBase):
    id: int
    is_active: bool
    class Config:
        from_attributes = True
