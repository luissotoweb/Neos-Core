"""
Schemas para el módulo de ventas
Validación con Pydantic para entrada/salida de datos
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from decimal import Decimal
from typing import Optional, List


# ============ SALE ITEM (Detalle de venta) ============

class SaleItemCreate(BaseModel):
    """Schema para crear un item de venta"""
    product_id: int = Field(..., gt=0, description="ID del producto")
    quantity: Decimal = Field(..., gt=0, description="Cantidad vendida")

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        """Valida que la cantidad no tenga más de 4 decimales"""
        if v.as_tuple().exponent < -4:
            raise ValueError("Cantidad: máximo 4 decimales permitidos")
        return v


class SaleItemResponse(BaseModel):
    """Schema de respuesta de item de venta"""
    id: int
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    tax_rate: Decimal
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    product_name: Optional[str] = None  # Se puede cargar desde el producto

    class Config:
        from_attributes = True


# ============ SALE (Venta) ============

class SaleCreate(BaseModel):
    """Schema para crear una venta nueva"""
    client_id: Optional[int] = Field(None, description="ID del cliente (opcional para consumidor final)")
    point_of_sale_id: int = Field(..., gt=0, description="ID del punto de venta")
    currency_id: int = Field(..., gt=0, description="ID de la moneda")
    exchange_rate: Decimal = Field(default=Decimal("1.0"), gt=0, description="Tasa de cambio")
    payment_method: str = Field(..., description="Método de pago")

    # Items de la venta
    items: List[SaleItemCreate] = Field(..., min_length=1, description="Debe tener al menos 1 producto")

    # Observaciones internas (opcional)
    notes: Optional[str] = Field(None, max_length=500)

    # Campos opcionales de facturación electrónica (CAE)
    # Solo se llenan si electronic_invoicing_enabled = True en el Tenant
    invoice_type: Optional[str] = Field(None, max_length=10, description="Tipo de comprobante: A, B, C")
    cae: Optional[str] = Field(None, max_length=50, description="CAE otorgado por ente fiscal")
    cae_expiration: Optional[datetime] = Field(None, description="Fecha de vencimiento del CAE")

    @field_validator('payment_method')
    @classmethod
    def validate_payment_method(cls, v):
        """Valida que el método de pago sea válido"""
        allowed = ['CASH', 'CARD', 'TRANSFER', 'DEBIT', 'CREDIT', 'CHECK', 'OTHER']
        if v.upper() not in allowed:
            raise ValueError(f"Método de pago inválido. Permitidos: {', '.join(allowed)}")
        return v.upper()


class SaleResponse(BaseModel):
    """Schema de respuesta completa de venta"""
    id: int
    tenant_id: int
    client_id: Optional[int]
    user_id: int
    point_of_sale_id: int
    currency_id: int
    exchange_rate: Decimal
    payment_method: str

    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal

    status: str
    notes: Optional[str]

    # Facturación electrónica (puede ser null)
    invoice_type: Optional[str]
    invoice_number: Optional[str]
    cae: Optional[str]
    cae_expiration: Optional[datetime]

    created_at: datetime
    updated_at: Optional[datetime]

    # Relaciones incluidas
    items: List[SaleItemResponse] = []

    class Config:
        from_attributes = True


class SaleListResponse(BaseModel):
    """Schema resumido para listar ventas (sin items, para performance)"""
    id: int
    invoice_number: Optional[str]
    total: Decimal
    payment_method: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============ FILTROS ============

class SaleFilters(BaseModel):
    """Filtros opcionales para búsqueda de ventas"""
    client_id: Optional[int] = None
    point_of_sale_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    payment_method: Optional[str] = None
    status: Optional[str] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)