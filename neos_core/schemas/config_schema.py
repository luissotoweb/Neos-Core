# neos_core/schemas/config_schema.py
"""
Schemas para configuración: Monedas y Puntos de Venta
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ============ MONEDAS ============

class CurrencyBase(BaseModel):
    """Campos base de moneda"""
    name: str = Field(..., min_length=1, max_length=50)
    code: str = Field(..., min_length=2, max_length=10, description="Ej: ARS, USD")
    symbol: str = Field(..., min_length=1, max_length=10, description="Ej: $, U$S")


class CurrencyCreate(CurrencyBase):
    """Schema para crear moneda"""
    is_active: bool = Field(default=True)

class CurrencyUpdate(BaseModel):
    """Schema para actualizar moneda"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    code: Optional[str] = Field(None, min_length=2, max_length=10, description="Ej: ARS, USD")
    symbol: Optional[str] = Field(None, min_length=1, max_length=10, description="Ej: $, U$S")
    is_active: Optional[bool] = None


class Currency(CurrencyBase):
    """Schema de respuesta de moneda"""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ PUNTOS DE VENTA ============

class PointOfSaleBase(BaseModel):
    """Campos base de punto de venta"""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20, description="Código único: POS-001")
    location: Optional[str] = Field(None, max_length=200, description="Dirección física")
    is_active: bool = Field(default=True)


class PointOfSaleCreate(PointOfSaleBase):
    """Schema para crear punto de venta"""
    tenant_id: int = Field(..., gt=0)


class PointOfSaleUpdate(BaseModel):
    """Schema para actualizar punto de venta"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=1, max_length=20, description="Código único: POS-001")
    location: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None


class PointOfSale(PointOfSaleBase):
    """Schema de respuesta de punto de venta"""
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
