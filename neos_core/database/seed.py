# neos_core/database/seed.py
"""
Seed unificado para poblar datos iniciales del sistema.
Compatible con TUS modelos exactos.
"""
from sqlalchemy.orm import Session
from decimal import Decimal
from neos_core.database.models import (
    Role,
    TaxIdType,
    TaxResponsibility,
    Currency,
    PointOfSale,
    Product,
    Tenant
)


def seed_roles(db: Session):
    """Crea los roles básicos del sistema"""
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
            print(f"✅ Rol creado: {r['name']}")

    db.commit()
    print("📋 Roles creados correctamente")


def seed_tax_data(db: Session):
    """Crea tipos de documento y responsabilidades fiscales"""

    # 1. Tipos de Documento (solo name, como en TU modelo)
    tax_types = ["CUIT", "CUIL", "DNI", "Pasaporte", "RUC", "RFC"]

    for name in tax_types:
        exists = db.query(TaxIdType).filter(TaxIdType.name == name).first()
        if not exists:
            db.add(TaxIdType(name=name))
            print(f"✅ Tipo fiscal creado: {name}")

    # 2. Responsabilidades Fiscales (solo name, como en TU modelo)
    responsibilities = [
        "Responsable Inscripto",
        "Monotributista",
        "Exento",
        "Consumidor Final"
    ]

    for name in responsibilities:
        exists = db.query(TaxResponsibility).filter(TaxResponsibility.name == name).first()
        if not exists:
            db.add(TaxResponsibility(name=name))
            print(f"✅ Responsabilidad fiscal creada: {name}")

    db.commit()
    print("🏛️ Datos fiscales creados correctamente")


def seed_currencies(db: Session):
    """Crea las monedas del sistema (usa TU modelo completo)"""
    currencies = [
        {"name": "Peso Argentino", "code": "ARS", "symbol": "$"},
        {"name": "Dólar Estadounidense", "code": "USD", "symbol": "U$S"},
        {"name": "Euro", "code": "EUR", "symbol": "€"},
        {"name": "Peso Mexicano", "code": "MXN", "symbol": "$"},
        {"name": "Peso Chileno", "code": "CLP", "symbol": "$"},
    ]

    for curr in currencies:
        exists = db.query(Currency).filter(Currency.code == curr["code"]).first()
        if not exists:
            # Crear con is_active si existe en tu modelo
            currency = Currency(**curr, is_active=True)
            db.add(currency)
            print(f"✅ Moneda creada: {curr['code']}")

    db.commit()
    print("💰 Monedas creadas correctamente")


def seed_point_of_sale(db: Session, tenant_id: int):
    """Crea un punto de venta de ejemplo (usa TU modelo con 'code')"""
    exists = db.query(PointOfSale).filter(
        PointOfSale.tenant_id == tenant_id,
        PointOfSale.code == "POS-001"
    ).first()

    if not exists:
        pos = PointOfSale(
            tenant_id=tenant_id,
            name="Caja Principal",
            code="POS-001",
            location="Local Central",
            is_active=True
        )
        db.add(pos)
        db.commit()
        print(f"✅ Punto de venta creado: {pos.name}")
        return pos
    else:
        print(f"ℹ️ Punto de venta ya existe: {exists.name}")
        return exists


def seed_products(db: Session, tenant_id: int):
    """Crea productos de ejemplo (usa TU modelo completo con JSONB)"""
    products_data = [
        {
            "sku": "PROD-001",
            "barcode": "7790001234567",
            "name": "Producto de Prueba 1",
            "description": "Producto físico con stock",
            "cost": Decimal("50.00"),
            "price": Decimal("100.00"),
            "stock": Decimal("100"),
            "min_stock": Decimal("10"),
            "tax_rate": Decimal("21.00"),
            "is_service": False,
            "product_type": "stock",
            "is_active": True,
            "attributes": {"color": "Rojo", "talla": "M"}
        },
        {
            "sku": "PROD-002",
            "barcode": "7790001234568",
            "name": "Producto de Prueba 2",
            "description": "Producto con IVA reducido",
            "cost": Decimal("80.00"),
            "price": Decimal("150.00"),
            "stock": Decimal("50"),
            "min_stock": Decimal("5"),
            "tax_rate": Decimal("10.50"),
            "is_service": False,
            "product_type": "stock",
            "is_active": True
        },
        {
            "sku": "SERV-001",
            "name": "Servicio de Consultoría",
            "description": "Servicio por hora (no mueve stock)",
            "cost": Decimal("0"),
            "price": Decimal("500.00"),
            "stock": Decimal("0"),
            "tax_rate": Decimal("21.00"),
            "is_service": True,
            "product_type": "service",
            "is_active": True
        }
    ]

    for prod_data in products_data:
        exists = db.query(Product).filter(
            Product.tenant_id == tenant_id,
            Product.sku == prod_data["sku"]
        ).first()

        if not exists:
            product = Product(tenant_id=tenant_id, **prod_data)
            db.add(product)
            print(f"✅ Producto creado: {prod_data['name']}")
        else:
            print(f"ℹ️ Producto ya existe: {exists.name}")

    db.commit()
    print("📦 Productos creados correctamente")


def run_full_seed(db: Session):
    """
    Ejecuta el seed completo del sistema.
    """
    print("\n" + "=" * 60)
    print("🌱 INICIANDO SEED COMPLETO DEL SISTEMA")
    print("=" * 60 + "\n")

    try:
        # 1. Seed de Roles
        print("📋 Paso 1/5: Creando Roles...")
        seed_roles(db)

        # 2. Seed de Datos Fiscales
        print("\n🏛️ Paso 2/5: Creando Datos Fiscales...")
        seed_tax_data(db)

        # 3. Seed de Monedas
        print("\n💰 Paso 3/5: Creando Monedas...")
        seed_currencies(db)

        # 4. Seed de Puntos de Venta (Solo si hay tenants activos)
        print("\n🏪 Paso 4/5: Creando Puntos de Venta...")
        tenant = db.query(Tenant).filter(Tenant.is_active == True).first()

        if tenant:
            print(f"   Usando tenant: {tenant.name} (ID: {tenant.id})")
            seed_point_of_sale(db, tenant.id)

            # 5. Seed de Productos
            print("\n📦 Paso 5/5: Creando Productos...")
            seed_products(db, tenant.id)
        else:
            print("   ⚠️ No hay tenants activos.")
            print("   👉 Crea un tenant primero para continuar con POS y Productos.")

        print("\n" + "=" * 60)
        print("✅ SEED COMPLETADO EXITOSAMENTE")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ ERROR DURANTE EL SEED: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise


# Para ejecutar directamente
if __name__ == "__main__":
    from neos_core.database.config import SessionLocal

    db = SessionLocal()
    try:
        run_full_seed(db)
    finally:
        db.close()
