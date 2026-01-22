"""
Endpoints mínimos de contabilidad (borradores y cierres de período)
"""
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from neos_core.crud import accounting_crud
from neos_core.database.config import get_db
from neos_core.database.models import User
from neos_core.schemas.accounting_schema import (
    AccountingClosePeriodRequest,
    AccountingClosePeriodResponse,
    AccountingDraftFilters,
    AccountingMoveResponse
)
from neos_core.security.security_deps import get_current_user

router = APIRouter(prefix="/accounting", tags=["Accounting"])


@router.get("/moves/drafts", response_model=List[AccountingMoveResponse])
def list_draft_moves(
    period_year: int | None = None,
    period_month: int | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    filters = AccountingDraftFilters(
        period_year=period_year,
        period_month=period_month,
        skip=skip,
        limit=limit
    )
    return accounting_crud.list_draft_moves(
        db=db,
        tenant_id=current_user.tenant_id,
        period_year=filters.period_year,
        period_month=filters.period_month,
        skip=filters.skip,
        limit=filters.limit
    )


@router.post("/periods/close", response_model=AccountingClosePeriodResponse)
def close_period(
    payload: AccountingClosePeriodRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    closed_at = datetime.utcnow()
    closed_moves = accounting_crud.close_period(
        db=db,
        tenant_id=current_user.tenant_id,
        period_year=payload.period_year,
        period_month=payload.period_month
    )
    return AccountingClosePeriodResponse(
        period_year=payload.period_year,
        period_month=payload.period_month,
        closed_moves=closed_moves,
        closed_at=closed_at
    )
