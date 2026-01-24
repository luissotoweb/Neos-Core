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


# --- TASAS DE IMPUESTO ---
@router.get("/tax-rates", response_model=List[schemas.TaxRate])
def read_tax_rates(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    return crud.get_tax_rates_by_tenant(db, tenant_id=current_user.tenant_id)


@router.post("/tax-rates", response_model=schemas.TaxRate)
def add_tax_rate(
        tax_rate: schemas.TaxRateCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    if current_user.role.name not in ["superadmin", "admin", "accountant"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para configurar tasas de impuesto")

    if current_user.role.name != "superadmin" and tax_rate.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="No puedes crear configuraciones para otra empresa")

    return crud.create_tax_rate(db, tax_rate)


@router.put("/tax-rates/{tax_rate_id}", response_model=schemas.TaxRate)
def update_tax_rate(
        tax_rate_id: int,
        tax_rate_update: schemas.TaxRateUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    if current_user.role.name not in ["superadmin", "admin", "accountant"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para configurar tasas de impuesto")

    return crud.update_tax_rate(
        db=db,
        tax_rate_id=tax_rate_id,
        tenant_id=current_user.tenant_id,
        tax_rate_update=tax_rate_update
    )


@router.delete("/tax-rates/{tax_rate_id}")
def delete_tax_rate(
        tax_rate_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    if current_user.role.name not in ["superadmin", "admin", "accountant"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para configurar tasas de impuesto")

    return {"success": crud.delete_tax_rate(db, tax_rate_id=tax_rate_id, tenant_id=current_user.tenant_id)}
