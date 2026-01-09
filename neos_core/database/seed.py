# neos_core/database/seed.py
from sqlalchemy.orm import Session
from neos_core.database.models.role_model import Role
from neos_core.database.models.tax_models import TaxIdType, TaxResponsibility, Currency

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

def seed_tax_data(db: Session):
    # 1. Tipos de Documento
    tax_types = ["CUIT", "CUIL", "DNI", "Pasaporte"]
    for name in tax_types:
        if not db.query(TaxIdType).filter(TaxIdType.name == name).first():
            db.add(TaxIdType(name=name))

    # 2. Responsabilidades Fiscales (Ejemplo Argentina)
    responsibilities = ["Responsable Inscripto", "Monotributista", "Exento", "Consumidor Final"]
    for name in responsibilities:
        if not db.query(TaxResponsibility).filter(TaxResponsibility.name == name).first():
            db.add(TaxResponsibility(name=name))

    # 3. Monedas
    currencies = [
        {"name": "Peso Argentino", "code": "ARS", "symbol": "$"},
        {"name": "Dólar Estadounidense", "code": "USD", "symbol": "U$S"}
    ]
    for curr in currencies:
        if not db.query(Currency).filter(Currency.code == curr["code"]).first():
            db.add(Currency(**curr))

    db.commit()