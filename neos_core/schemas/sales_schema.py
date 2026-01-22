"""
Schemas para el módulo de ventas
Validación con Pydantic para entrada/salida de datos
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Literal


# ============ SALE ITEM ============

class SaleItemCreate(BaseModel):
    product_id: int = Field(..., gt=0, description="ID del producto")
    quantity: Decimal = Field(..., gt=0, description="Cantidad vendida")

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: Decimal):
        if v.as_tuple().exponent < -4:
            raise ValueError("Cantidad: máximo 4 decimales permitidos")
        return v


class SaleItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    product_name: Optional[str] = None

    class Config:
        from_attributes = True


# ============ SALE ============

SaleStatus = Literal["completed", "cancelled", "on_hold"]

class SaleCreate(BaseModel):
    client_id: Optional[int] = Field(None, description="Cliente opcional")
    point_of_sale_id: int = Field(..., gt=0)
    currency_id: int = Field(..., gt=0)
    payment_method: str = Field(..., min_length=2, max_length=50)
    items: List[SaleItemCreate]

    @field_validator("items")
    @classmethod
    def validate_items_not_empty(cls, v):
        if not v:
            raise ValueError("La venta debe tener al menos un item")
        return v


class SaleResponse(BaseModel):
    id: int
    tenant_id: int
    user_id: int
    client_id: Optional[int]
    point_of_sale_id: int
    currency_id: int
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    payment_method: str
    status: SaleStatus
    created_at: datetime
    items: List[SaleItemResponse]

    class Config:
        from_attributes = True


class SaleListResponse(BaseModel):
    id: int
    total: Decimal
    status: SaleStatus
    created_at: datetime

    class Config:
        from_attributes = True


class SaleFilters(BaseModel):
    client_id: Optional[int] = None
    point_of_sale_id: Optional[int] = None
    payment_method: Optional[str] = None
    status: Optional[SaleStatus] = None
    skip: int = 0
    limit: int = Field(default=50, ge=1, le=100)
