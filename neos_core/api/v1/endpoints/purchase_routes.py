from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from neos_core.database.config import get_db
from neos_core.database.models import User
from neos_core.security.security_deps import get_current_user
from neos_core.schemas.purchase_schema import PurchaseCreate, PurchaseResponse
from neos_core.crud import purchase_crud

router = APIRouter(prefix="/purchases", tags=["Purchases"])


def check_purchase_permission(current_user: User = Depends(get_current_user)):
    allowed_roles = ["admin", "superadmin", "accountant"]

    if current_user.role.name not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso denegado"
        )
    return current_user


@router.post("/", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
def create_purchase(
    purchase_data: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_purchase_permission)
):
    return purchase_crud.create_purchase(
        db=db,
        purchase_data=purchase_data,
        tenant_id=current_user.tenant_id
    )


@router.get("/{purchase_id}", response_model=PurchaseResponse)
def get_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    purchase = purchase_crud.get_purchase_by_id(db, purchase_id, current_user.tenant_id)
    if not purchase:
        raise HTTPException(404, "Compra no encontrada")
    return purchase


@router.get("/", response_model=List[PurchaseResponse])
def list_purchases(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return purchase_crud.get_purchases(db, current_user.tenant_id, skip=skip, limit=limit)
