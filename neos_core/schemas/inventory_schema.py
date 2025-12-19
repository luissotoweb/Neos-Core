# neos_core/schemas/inventory_schema.py
from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    price: float = 0.0
    stock: int = 0

class ProductCreate(ProductBase):
    tenant_id: int  # Obligatorio para vincular al cliente

class Product(ProductBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True