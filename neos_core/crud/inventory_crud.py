# neos_core/crud/inventory_crud.py
from sqlalchemy.orm import Session
from neos_core.database.models.inventory_model import Product
from neos_core.schemas.inventory_schema import ProductCreate

def create_product(db: Session, product: ProductCreate):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products_by_tenant(db: Session, tenant_id: int, skip: int = 0, limit: int = 100):
    return db.query(Product).filter(Product.tenant_id == tenant_id).offset(skip).limit(limit).all()

def get_product_by_id(db: Session, product_id: int, tenant_id: int):
    # Siempre filtramos por tenant_id para evitar que alguien vea productos ajenos por ID
    return db.query(Product).filter(Product.id == product_id, Product.tenant_id == tenant_id).first()