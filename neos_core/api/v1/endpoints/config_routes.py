from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from neos_core.database.config import get_db
from neos_core.security.security_deps import get_current_user
from neos_core.database import models
from neos_core.schemas import config_schema as schemas
from neos_core.crud import config_crud as crud

router = APIRouter()


# --- MONEDAS ---
@router.get("/currencies", response_model=List[schemas.Currency])
def read_currencies(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Todos pueden leer monedas
    return crud.get_currencies(db)


@router.post("/currencies", response_model=schemas.Currency)
def add_currency(currency: schemas.CurrencyCreate, db: Session = Depends(get_db),
                 current_user: models.User = Depends(get_current_user)):
    # SOLO SuperAdmin puede crear monedas
    if current_user.role.name != "superadmin":
        raise HTTPException(status_code=403, detail="Permiso denegado: Solo el SuperAdmin define monedas")
    return crud.create_currency(db, currency)


@router.put("/currencies/{currency_id}", response_model=schemas.Currency)
@router.patch("/currencies/{currency_id}", response_model=schemas.Currency)
def update_currency(
        currency_id: int,
        currency_update: schemas.CurrencyUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    if current_user.role.name != "superadmin":
        raise HTTPException(status_code=403, detail="Permiso denegado: Solo el SuperAdmin define monedas")
    return crud.update_currency(db, currency_id, currency_update)


# --- PUNTOS DE VENTA ---
@router.get("/pos", response_model=List[schemas.PointOfSale])
def read_my_pos(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Cada uno ve los POS de su propia empresa
    return crud.get_pos_by_tenant(db, tenant_id=current_user.tenant_id)


@router.post("/pos", response_model=schemas.PointOfSale)
def add_pos(pos: schemas.PointOfSaleCreate, db: Session = Depends(get_db),
            current_user: models.User = Depends(get_current_user)):
    # Admin y Accountant pueden administrar POS de su Tenant
    if current_user.role.name not in ["superadmin", "admin", "accountant"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para configurar Puntos de Venta")

    # Seguridad: Un Admin no puede crear POS para otro Tenant
    if current_user.role.name != "superadmin" and pos.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="No puedes crear configuraciones para otra empresa")

    return crud.create_pos(db, pos)


@router.put("/pos/{pos_id}", response_model=schemas.PointOfSale)
@router.patch("/pos/{pos_id}", response_model=schemas.PointOfSale)
def update_pos(
        pos_id: int,
        pos_update: schemas.PointOfSaleUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    if current_user.role.name not in ["superadmin", "admin", "accountant"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para configurar Puntos de Venta")

    if current_user.role.name == "superadmin":
        db_pos = crud.get_pos_by_id_global(db, pos_id=pos_id)
    else:
        db_pos = crud.get_pos_by_id(db, pos_id=pos_id, tenant_id=current_user.tenant_id)

    if not db_pos:
        raise HTTPException(status_code=404, detail="Punto de venta no encontrado")

    if current_user.role.name != "superadmin" and db_pos.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="No puedes actualizar configuraciones de otra empresa")

    return crud.update_pos(db, pos_id=db_pos.id, tenant_id=db_pos.tenant_id, pos_update=pos_update)
