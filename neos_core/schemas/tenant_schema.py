from pydantic import BaseModel
from typing import Optional

class TenantBase(BaseModel):
    name: str
    description: Optional[str] = None

class TenantCreate(TenantBase):
    pass

class Tenant(TenantBase):
    id: int
    is_active: bool
    class Config:
        from_attributes = True