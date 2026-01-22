# neos_core/schemas/product_schema.py
"""
Schemas para productos (inventario)
Usa Decimal para precisión monetaria
"""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime


class ProductBase(BaseModel):
    """Campos base de producto"""
    sku: str = Field(..., min_length=1, max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None

    # Precios con Decimal (NO float)
    price: Decimal = Field(..., ge=0, description="Precio de venta")
    cost: Decimal = Field(default=Decimal("0"), ge=0, description="Costo de compra")

    # Stock con Decimal (permite fracciones: 2.5 kg)
    stock: Decimal = Field(default=Decimal("0"), ge=0)
    min_stock: Optional[Decimal] = Field(None, ge=0, description="Stock mínimo de alerta")

    # Unidades y conversión
    purchase_unit: str = Field(default="unit", min_length=1, max_length=50)
    sale_unit: str = Field(default="unit", min_length=1, max_length=50)
    conversion_factor: Decimal = Field(
        default=Decimal("1"),
        gt=0,
        description="Equivalencia de unidad de venta a unidad de compra"
    )

    # Impuestos
    tax_rate: Decimal = Field(default=Decimal("0"), ge=0, le=100, description="Tasa de impuesto (%)")

    # Flags
    is_service: bool = Field(default=False, description="True si es un servicio (no mueve stock)")
    is_active: bool = Field(default=True)

    # Atributos dinámicos (JSONB)
    attributes: Optional[dict] = Field(None, description="Atributos custom como color, talla, etc.")


class ProductCreate(ProductBase):
    """Schema para crear producto (requiere tenant_id)"""
    tenant_id: int = Field(..., gt=0)


class ProductUpdate(BaseModel):
    """Schema para actualizar producto (todos los campos opcionales)"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    cost: Optional[Decimal] = Field(None, ge=0)
    stock: Optional[Decimal] = Field(None, ge=0)
    min_stock: Optional[Decimal] = Field(None, ge=0)
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None
    attributes: Optional[dict] = None
    purchase_unit: Optional[str] = Field(None, min_length=1, max_length=50)
    sale_unit: Optional[str] = Field(None, min_length=1, max_length=50)
    conversion_factor: Optional[Decimal] = Field(None, gt=0)


class Product(ProductBase):
    """Schema de respuesta de producto"""
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema resumido para listados (sin todos los campos)"""
    id: int
    sku: str
    name: str
    price: Decimal
    stock: Decimal
    is_active: bool

    class Config:
        from_attributes = True
