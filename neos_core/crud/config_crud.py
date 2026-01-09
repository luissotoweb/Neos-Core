from sqlalchemy.orm import Session
from neos_core.database.models import tax_models as models
from neos_core.schemas import config_schema as schemas

# --- CRUD Monedas ---
def get_currencies(db: Session):
    return db.query(models.Currency).all()

def create_currency(db: Session, currency: schemas.CurrencyCreate):
    db_currency = models.Currency(**currency.model_dump())
    db.add(db_currency)
    db.commit()
    db.refresh(db_currency)
    return db_currency

# --- CRUD Puntos de Venta ---
def get_pos_by_tenant(db: Session, tenant_id: int):
    return db.query(models.PointOfSale).filter(models.PointOfSale.tenant_id == tenant_id).all()

def create_pos(db: Session, pos: schemas.PointOfSaleCreate):
    db_pos = models.PointOfSale(**pos.model_dump())
    db.add(db_pos)
    db.commit()
    db.refresh(db_pos)
    return db_pos