from sqlalchemy.orm import Session
from neos_core.database.models import client_model as models
from neos_core.schemas import client_schema as schemas

def create_client(db: Session, client: schemas.ClientCreate):
    db_client = models.Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def get_clients_by_tenant(db: Session, tenant_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Client).filter(models.Client.tenant_id == tenant_id).offset(skip).limit(limit).all()

def get_client_by_tax_id(db: Session, tax_id: str, tenant_id: int):
    return db.query(models.Client).filter(
        models.Client.tax_id == tax_id,
        models.Client.tenant_id == tenant_id
    ).first()