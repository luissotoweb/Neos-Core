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

@router.get("/{tenant_id}", response_model=schemas.Tenant)
def read_tenant(tenant_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role.name != "superadmin" and current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="No tienes acceso.")
    db_tenant = crud.get_tenant_by_id(db, tenant_id=tenant_id)
    if not db_tenant: raise HTTPException(status_code=404)
    return db_tenant