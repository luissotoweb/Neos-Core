from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str
    tenant_id: int
    role_id: int  # <--- Requerido para asignar el rol al crear

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    tenant_id: int
    role_id: int
    created_at: datetime

    class Config:
        from_attributes = True
