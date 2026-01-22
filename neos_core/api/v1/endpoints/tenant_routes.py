from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from neos_core import schemas, crud
from neos_core.database import models
from neos_core.database.config import get_db
from neos_core.security.security_deps import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.Tenant, status_code=201)
def create_new_tenant(tenant: schemas.TenantCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role.name != "superadmin":
        raise HTTPException(status_code=403, detail="Solo SuperAdmin.")
    return crud.create_tenant(db=db, tenant=tenant)


@router.post("/onboarding", response_model=schemas.TenantOnboardingResponse, status_code=201)
def create_tenant_onboarding(
    tenant: schemas.TenantOnboardingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role.name != "superadmin":
        raise HTTPException(status_code=403, detail="Solo SuperAdmin.")

    preset = crud.ensure_onboarding_preset(db, rubro=tenant.rubro)
    if not preset:
        raise HTTPException(status_code=400, detail="Rubro no soportado.")

    db_tenant = crud.create_tenant(
        db=db,
        tenant=schemas.TenantCreate(
            name=tenant.name,
            description=tenant.description,
            tax_id=tenant.tax_id,
            tax_id_type_id=tenant.tax_id_type_id,
            tax_responsibility_id=tenant.tax_responsibility_id,
        ),
    )

    onboarding = crud.create_tenant_onboarding_config(
        db=db,
        tenant_id=db_tenant.id,
        rubro=tenant.rubro,
        categories=preset.categories,
        active_modules=preset.active_modules,
        preset_id=preset.id,
    )

    return schemas.TenantOnboardingResponse(
        tenant=db_tenant,
        onboarding=schemas.TenantOnboardingConfig(
            rubro=onboarding.rubro,
            categories=onboarding.categories,
            active_modules=onboarding.active_modules,
        ),
    )

@router.get("/{tenant_id}", response_model=schemas.Tenant)
def read_tenant(tenant_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role.name != "superadmin" and current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="No tienes acceso.")
    db_tenant = crud.get_tenant_by_id(db, tenant_id=tenant_id)
    if not db_tenant: raise HTTPException(status_code=404)
    return db_tenant

@router.get("/", response_model=list[schemas.Tenant])
def read_tenants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role.name != "superadmin":
        raise HTTPException(status_code=403, detail="Acceso denegado.")
    return crud.get_tenants(db, skip=skip, limit=limit)
