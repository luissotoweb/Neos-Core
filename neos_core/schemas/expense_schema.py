from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class ExpenseBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=0)


class ExpenseCreate(ExpenseBase):
    tenant_id: int = Field(..., gt=0)
    suggested_account: Optional[str] = Field(None, max_length=50)


class ExpenseResponse(ExpenseBase):
    id: int
    tenant_id: int
    suggested_account: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ExpenseSuggestionRequest(ExpenseBase):
    pass


class ExpenseSuggestionResponse(BaseModel):
    provider: str
    model: Optional[str] = None
    suggested_account: Optional[str] = None
    expense: ExpenseResponse
    raw_response: str
