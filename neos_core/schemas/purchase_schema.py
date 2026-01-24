from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class PurchaseBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=0)
    supplier_name: Optional[str] = Field(None, max_length=255)


class PurchaseCreate(PurchaseBase):
    tenant_id: int = Field(..., gt=0)
    currency_id: int = Field(..., gt=0)
    suggested_account: Optional[str] = Field(None, max_length=50)


class PurchaseResponse(PurchaseBase):
    id: int
    tenant_id: int
    currency_id: int
    suggested_account: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
