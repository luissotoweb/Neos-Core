# neos_core/crud/tenant_crud.py

from sqlalchemy.orm import Session
from neos_core.database import models
from neos_core.schemas import tenant_schema as schemas

def get_tenant_by_name(db: Session, name: str):
    """Busca un Tenant por su nombre."""
    return db.query(models.Tenant).filter(models.Tenant.name == name).first()

def get_tenant_by_id(db: Session, tenant_id: int):
    """Busca un Tenant por su ID principal."""
    return db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()

def create_tenant(db: Session, tenant: schemas.TenantCreate):
    """Crea un nuevo Tenant en la base de datos."""
    db_tenant = models.Tenant(**tenant.model_dump())
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant


def get_tenants(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Tenant).offset(skip).limit(limit).all()