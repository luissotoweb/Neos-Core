# neos_core/schemas/config_schema.py
"""
Schemas para configuración: Monedas y Puntos de Venta
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


# ============ MONEDAS ============

class CurrencyBase(BaseModel):
    """Campos base de moneda"""
    name: str = Field(..., min_length=1, max_length=50)
    code: str = Field(..., min_length=2, max_length=10, description="Ej: ARS, USD")
    symbol: str = Field(..., min_length=1, max_length=10, description="Ej: $, U$S")


class CurrencyCreate(CurrencyBase):
    """Schema para crear moneda"""
    is_active: bool = Field(default=True)


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


# ============ TASAS DE IMPUESTO ============

class TaxRateBase(BaseModel):
    """Campos base de tasa de impuesto"""
    name: str = Field(..., min_length=1, max_length=100)
    rate: Decimal = Field(..., ge=0, le=100, description="Porcentaje de impuesto")
    is_active: bool = Field(default=True)


class TaxRateCreate(TaxRateBase):
    """Schema para crear tasa de impuesto"""
    tenant_id: int = Field(..., gt=0)


class TaxRateUpdate(BaseModel):
    """Schema para actualizar tasa de impuesto"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    rate: Optional[Decimal] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None


class TaxRate(TaxRateBase):
    """Schema de respuesta de tasa de impuesto"""
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
