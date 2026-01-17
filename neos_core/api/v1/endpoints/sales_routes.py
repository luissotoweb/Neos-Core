"""
Endpoints de ventas con validación de permisos por rol
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from neos_core.database.config import get_db
from neos_core.database.models import User
from neos_core.security.security_deps import get_current_user
from neos_core.schemas.sales_schema import (
    SaleCreate,
    SaleResponse,
    SaleListResponse,
    SaleFilters
)
from neos_core.crud import sales_crud

router = APIRouter(prefix="/sales", tags=["Sales"])


# ===== DEPENDENCIA DE PERMISOS =====
def check_sale_permission(current_user: User = Depends(get_current_user)):
    """
    Verifica que el usuario tenga permisos para realizar ventas.
    Roles permitidos: seller, admin, superadmin
    """
    allowed_roles = ["seller", "admin", "superadmin"]

    if current_user.role.name not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permiso denegado. Roles permitidos: {', '.join(allowed_roles)}"
        )

    return current_user


# ===== ENDPOINTS =====

@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(
        sale_data: SaleCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_sale_permission)
):
    """
    Crea una nueva venta.

    **Permisos requeridos:** seller, admin, superadmin

    **Validaciones:**
    - Stock suficiente
    - Pertenencia al tenant de todos los recursos
    - Configuración de facturación electrónica si aplica

    **Operación atómica:** Si falla algo, se revierte todo (rollback).
    """
    sale = sales_crud.create_sale(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        sale_data=sale_data
    )

    return sale


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
        sale_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Obtiene una venta por ID.

    **Aislamiento:** Solo puede ver ventas de su propio tenant.
    """
    sale = sales_crud.get_sale_by_id(db, sale_id, current_user.tenant_id)

    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada"
        )

    return sale


@router.get("/", response_model=List[SaleListResponse])
def list_sales(
        client_id: int = None,
        point_of_sale_id: int = None,
        payment_method: str = None,
        status: str = None,
        skip: int = 0,
        limit: int = 50,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Lista ventas con filtros opcionales.

    **Filtros disponibles:**
    - client_id: Ventas de un cliente específico
    - point_of_sale_id: Ventas de un punto de venta
    - payment_method: Por método de pago
    - status: completed, cancelled, pending

    **Paginación:** skip y limit
    """
    filters = SaleFilters(
        client_id=client_id,
        point_of_sale_id=point_of_sale_id,
        payment_method=payment_method,
        status=status,
        skip=skip,
        limit=limit
    )

    sales = sales_crud.get_sales(db, current_user.tenant_id, filters)

    return sales


@router.post("/{sale_id}/cancel", response_model=SaleResponse)
def cancel_sale(
        sale_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_sale_permission)
):
    """
    Cancela una venta y revierte el stock.

    **Permisos requeridos:** seller, admin, superadmin

    **Validaciones:**
    - Solo se pueden cancelar ventas en estado "completed"
    - Se revierte el stock automáticamente
    """
    sale = sales_crud.cancel_sale(
        db=db,
        sale_id=sale_id,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )

    return sale