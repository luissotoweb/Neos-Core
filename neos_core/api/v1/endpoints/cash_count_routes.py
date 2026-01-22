"""
Endpoints de cierre de caja.
"""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from neos_core.database.config import get_db
from neos_core.database.models import User
from neos_core.security.security_deps import get_current_user
from neos_core.schemas.cash_count_schema import CashCountCreate, CashCountResponse
from neos_core.crud import cash_count_crud

router = APIRouter(prefix="/cash-counts", tags=["Cash Counts"])


def check_cash_count_permission(current_user: User = Depends(get_current_user)):
    allowed_roles = ["seller", "admin", "superadmin"]

    if current_user.role.name not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso denegado"
        )
    return current_user


@router.post("/", response_model=CashCountResponse, status_code=status.HTTP_201_CREATED)
def create_cash_count(
    cash_count_data: CashCountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_cash_count_permission)
):
    return cash_count_crud.create_cash_count(
        db=db,
        tenant_id=current_user.tenant_id,
        cash_count_data=cash_count_data
    )


@router.get("/", response_model=CashCountResponse)
def get_cash_count(
    point_of_sale_id: int,
    count_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cash_count = cash_count_crud.get_cash_count(
        db=db,
        tenant_id=current_user.tenant_id,
        point_of_sale_id=point_of_sale_id,
        count_date=count_date
    )
    if not cash_count:
        raise HTTPException(404, "Cierre de caja no encontrado")
    return cash_count
