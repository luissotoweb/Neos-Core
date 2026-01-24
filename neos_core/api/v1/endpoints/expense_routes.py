from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from neos_core.database.config import get_db
from neos_core.database.models import User
from neos_core.security.security_deps import get_current_user
from neos_core.schemas.expense_schema import ExpenseCreate, ExpenseResponse
from neos_core.crud import expense_crud

router = APIRouter(prefix="/expenses", tags=["Expenses"])


def check_expense_permission(current_user: User = Depends(get_current_user)):
    allowed_roles = ["admin", "superadmin", "accountant"]

    if current_user.role.name not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso denegado"
        )
    return current_user


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_expense_permission)
):
    return expense_crud.create_expense(
        db=db,
        expense_data=expense_data,
        tenant_id=current_user.tenant_id
    )


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = expense_crud.get_expense_by_id(db, expense_id, current_user.tenant_id)
    if not expense:
        raise HTTPException(404, "Gasto no encontrado")
    return expense


@router.get("/", response_model=List[ExpenseResponse])
def list_expenses(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return expense_crud.get_expenses(db, current_user.tenant_id, skip=skip, limit=limit)
