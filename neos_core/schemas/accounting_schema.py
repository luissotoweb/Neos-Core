from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Literal

from pydantic import BaseModel, Field


AccountingStatus = Literal["draft", "posted"]


class AccountingLineResponse(BaseModel):
    id: int
    account_code: str
    description: Optional[str]
    debit: Decimal
    credit: Decimal

    class Config:
        from_attributes = True


class AccountingMoveResponse(BaseModel):
    id: int
    tenant_id: int
    sale_id: Optional[int]
    currency_id: int
    description: Optional[str]
    status: AccountingStatus
    move_date: datetime
    period_year: int
    period_month: int
    posted_at: Optional[datetime]
    lines: List[AccountingLineResponse]

    class Config:
        from_attributes = True


class AccountingDraftFilters(BaseModel):
    period_year: Optional[int] = Field(default=None, ge=2000)
    period_month: Optional[int] = Field(default=None, ge=1, le=12)
    skip: int = 0
    limit: int = Field(default=50, ge=1, le=100)


class AccountingClosePeriodRequest(BaseModel):
    period_year: int = Field(..., ge=2000)
    period_month: int = Field(..., ge=1, le=12)


class AccountingClosePeriodResponse(BaseModel):
    period_year: int
    period_month: int
    closed_moves: int
    closed_at: datetime
