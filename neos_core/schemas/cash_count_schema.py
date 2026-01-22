"""
Schemas para cierre de caja.
"""
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CashCountCreate(BaseModel):
    point_of_sale_id: int = Field(..., gt=0)
    count_date: date
    counted_amount: Decimal = Field(..., ge=0)


class CashCountResponse(BaseModel):
    id: int
    tenant_id: int
    point_of_sale_id: int
    count_date: date
    counted_amount: Decimal
    recorded_amount: Decimal
    difference: Decimal
    created_at: datetime

    class Config:
        from_attributes = True
