# neos_core/database/seed.py
from sqlalchemy.orm import Session
from neos_core.database.models.role_model import Role

def seed_roles(db: Session):
    roles = [
        {"name": "superadmin", "description": "Acceso total al SaaS"},
        {"name": "admin", "description": "Administrador del Tenant"},
        {"name": "inventory", "description": "Gestión de Stock"},
        {"name": "accountant", "description": "Contabilidad y Reportes"},
        {"name": "seller", "description": "Ventas y pedidos"}
    ]
    for r in roles:
        exists = db.query(Role).filter(Role.name == r["name"]).first()
        if not exists:
            db.add(Role(**r))
    db.commit()