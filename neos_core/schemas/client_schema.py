from pydantic import BaseModel, EmailStr
from typing import Optional

class ClientBase(BaseModel):
    full_name: str
    tax_id_type_id: int
    tax_id: str
    tax_responsibility_id: int
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    phone: Optional[str] = None

class ClientCreate(ClientBase):
    tenant_id: int

class ClientUpdate(BaseModel):
    full_name: Optional[str] = None
    tax_id_type_id: Optional[int] = None
    tax_id: Optional[str] = None
    tax_responsibility_id: Optional[int] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    phone: Optional[str] = None

class Client(ClientBase):
    id: int
    tenant_id: int

    model_config = {"from_attributes": True}
