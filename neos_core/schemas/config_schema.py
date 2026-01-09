from pydantic import BaseModel
from typing import Optional

# --- Monedas ---
class CurrencyBase(BaseModel):
    name: str
    code: str  # Ejemplo: "ARS", "USD"
    symbol: str # Ejemplo: "$", "U$S"

class CurrencyCreate(CurrencyBase):
    pass

class Currency(CurrencyBase):
    id: int
    class Config:
        from_attributes = True

# --- Puntos de Venta (POS) ---
class PointOfSaleBase(BaseModel):
    number: int
    name: str
    is_active: Optional[bool] = True

class PointOfSaleCreate(PointOfSaleBase):
    tenant_id: int

class PointOfSale(PointOfSaleBase):
    id: int
    tenant_id: int
    class Config:
        from_attributes = True