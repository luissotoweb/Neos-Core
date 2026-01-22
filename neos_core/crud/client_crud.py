from sqlalchemy.orm import Session
from typing import Optional
from neos_core.database.models import client_model as models
from neos_core.schemas import client_schema as schemas

def create_client(db: Session, client: schemas.ClientCreate):
    db_client = models.Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def get_clients_by_tenant(
    db: Session,
    tenant_id: int,
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
):
    query = db.query(models.Client).filter(models.Client.tenant_id == tenant_id)
    if not include_inactive:
        query = query.filter(models.Client.is_active.is_(True))
    return query.offset(skip).limit(limit).all()

def get_client_by_tax_id(db: Session, tax_id: str, tenant_id: int):
    return db.query(models.Client).filter(
        models.Client.tax_id == tax_id,
        models.Client.tenant_id == tenant_id
    ).first()

def get_client_by_id(db: Session, client_id: int, tenant_id: Optional[int] = None):
    query = db.query(models.Client).filter(models.Client.id == client_id)
    if tenant_id is not None:
        query = query.filter(models.Client.tenant_id == tenant_id)
    return query.first()


def update_client(db: Session, db_client: models.Client, client_update: schemas.ClientUpdate):
    update_data = client_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_client, field, value)
    db.commit()
    db.refresh(db_client)
    return db_client


def soft_delete_client(db: Session, client_id: int, tenant_id: Optional[int] = None):
    query = db.query(models.Client).filter(models.Client.id == client_id)
    if tenant_id is not None:
        query = query.filter(models.Client.tenant_id == tenant_id)
    db_client = query.first()
    if not db_client:
        return None
    db_client.is_active = False
    db.commit()
    db.refresh(db_client)
    return db_client
