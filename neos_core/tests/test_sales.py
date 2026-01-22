"""
Tests completos para el módulo de ventas
Compatible con tu estructura actual de tests
"""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from neos_core.database.models import (
    Tenant, User, Role, Product, Client, ProductKit,
    PointOfSale, Currency, Sale, SaleDetail,
    TaxIdType, TaxResponsibility, ProductType
)
from neos_core.crud.user_crud import get_password_hash


def get_token(client, email: str, password: str):
    """Helper para obtener token de autenticación"""
    response = client.post("/token", data={
        "username": email,
        "password": password
    })
    if response.status_code != 200:
        raise Exception(f"Login failed: {response.json()}")
    return response.json()["access_token"]


# ===== FIXTURES ESPECÍFICAS PARA VENTAS =====

@pytest.fixture
def sales_setup(db):
    """
    Setup completo para tests de ventas
    Reutiliza seed_data si existe, o crea desde cero
    """
    # 1. Verificar/Crear Roles
    role_seller = db.query(Role).filter(Role.name == "seller").first()
    role_admin = db.query(Role).filter(Role.name == "admin").first()

    if not role_seller:
        role_seller = Role(name="seller", description="Vendedor")
        db.add(role_seller)
    if not role_admin:
        role_admin = Role(name="admin", description="Administrador")
        db.add(role_admin)

    db.commit()

    # 2. Crear datos fiscales
    tax_type = TaxIdType(name="CUIT")
    tax_resp = TaxResponsibility(name="Responsable Inscripto")
    db.add_all([tax_type, tax_resp])
    db.commit()

    # 3. Crear Tenants
    tenant_a = Tenant(
        name="Empresa Ventas A",
        tax_id="20-12345678-9",
        is_active=True,
        electronic_invoicing_enabled=False
    )
    tenant_b = Tenant(
        name="Empresa Ventas B",
        tax_id="20-98765432-1",
        is_active=True,
        electronic_invoicing_enabled=True,
        electronic_invoicing_provider="AFIP"
    )
    db.add_all([tenant_a, tenant_b])
    db.commit()

    # 4. Crear Usuarios
    user_seller_a = User(
        email="seller.sales@empresaa.com",
        hashed_password=get_password_hash("password123"),
        full_name="Juan Vendedor",
        tenant_id=tenant_a.id,
        role_id=role_seller.id,
        is_active=True
    )
    user_admin_b = User(
        email="admin.sales@empresab.com",
        hashed_password=get_password_hash("password123"),
        full_name="María Admin",
        tenant_id=tenant_b.id,
        role_id=role_admin.id,
        is_active=True
    )
    db.add_all([user_seller_a, user_admin_b])
    db.commit()

    # 5. Crear Moneda
    currency = db.query(Currency).filter(Currency.code == "ARS").first()
    if not currency:
        currency = Currency(code="ARS", name="Peso Argentino", symbol="$", is_active=True)
        db.add(currency)
        db.commit()

    # 6. Crear Puntos de Venta
    pos_a = PointOfSale(
        tenant_id=tenant_a.id,
        name="Caja Ventas 1",
        code="SALES-001",
        is_active=True
    )
    pos_b = PointOfSale(
        tenant_id=tenant_b.id,
        name="Caja Ventas Principal",
        code="SALES-001",
        is_active=True
    )
    db.add_all([pos_a, pos_b])
    db.commit()

    # 7. Crear Productos
    product_a = Product(
        tenant_id=tenant_a.id,
        sku="SALES-PROD-001",
        name="Producto Venta A",
        price=Decimal("100.00"),
        cost=Decimal("50.00"),
        stock=Decimal("50"),
        tax_rate=Decimal("21.00"),
        is_active=True
    )
    product_b = Product(
        tenant_id=tenant_b.id,
        sku="SALES-PROD-002",
        name="Producto Venta B",
        price=Decimal("200.00"),
        cost=Decimal("100.00"),
        stock=Decimal("10"),
        tax_rate=Decimal("10.50"),
        is_active=True
    )
    db.add_all([product_a, product_b])
    db.commit()

    # 8. Crear Cliente
    client_a = Client(
        tenant_id=tenant_a.id,
        full_name="Cliente Ventas Test",
        tax_id="20-11111111-1",
        tax_id_type_id=tax_type.id,
        tax_responsibility_id=tax_resp.id,
        email="cliente@test.com"
    )
    db.add(client_a)
    db.commit()

    return {
        "tenant_a": tenant_a,
        "tenant_b": tenant_b,
        "user_seller_a": user_seller_a,
        "user_admin_b": user_admin_b,
        "currency": currency,
        "pos_a": pos_a,
        "pos_b": pos_b,
        "product_a": product_a,
        "product_b": product_b,
        "client_a": client_a,
    }


# ===== TESTS DE CREACIÓN DE VENTAS =====

def test_create_sale_success(client, db, sales_setup):
    """✅ Flujo feliz: Crear venta correctamente"""
    token = get_token(client, "seller.sales@empresaa.com", "password123")

    sale_data = {
        "client_id": sales_setup["client_a"].id,
        "point_of_sale_id": sales_setup["pos_a"].id,
        "currency_id": sales_setup["currency"].id,
        "exchange_rate": 1.0,
        "payment_method": "CASH",
        "items": [
            {
                "product_id": sales_setup["product_a"].id,
                "quantity": 5
            }
        ]
    }

    response = client.post(
        "/api/v1/sales/",
        json=sale_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()

    # Verificar cálculos
    assert float(data["subtotal"]) == 500.00  # 100 * 5
    assert float(data["tax_amount"]) == 105.00  # 500 * 0.21
    assert float(data["total"]) == 605.00
    assert data["status"] == "completed"
    assert len(data["items"]) == 1

    # Verificar descuento de stock
    product = db.query(Product).filter(
        Product.id == sales_setup["product_a"].id
    ).first()
    assert float(product.stock) == 45.0  # 50 - 5


def test_create_sale_insufficient_stock(client, sales_setup):
    """❌ Error: Stock insuficiente"""
    token = get_token(client, "seller.sales@empresaa.com", "password123")

    sale_data = {
        "point_of_sale_id": sales_setup["pos_a"].id,
        "currency_id": sales_setup["currency"].id,
        "payment_method": "CASH",
        "items": [
            {
                "product_id": sales_setup["product_a"].id,
                "quantity": 100  # Más de lo disponible (50)
            }
        ]
    }

    response = client.post(
        "/api/v1/sales/",
        json=sale_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert "Stock insuficiente" in response.json()["detail"]


def test_create_sale_product_from_other_tenant(client, sales_setup):
    """❌ Seguridad: No puede vender producto de otro tenant"""
    token = get_token(client, "seller.sales@empresaa.com", "password123")

    sale_data = {
        "point_of_sale_id": sales_setup["pos_a"].id,
        "currency_id": sales_setup["currency"].id,
        "payment_method": "CASH",
        "items": [
            {
                "product_id": sales_setup["product_b"].id,  # Producto de Tenant B
                "quantity": 1
            }
        ]
    }

    response = client.post(
        "/api/v1/sales/",
        json=sale_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    assert "no pertenece" in response.json()["detail"].lower()


def test_create_sale_with_conversion_factor_stock_deduction(client, db, sales_setup):
    """✅ Descuenta stock usando conversion_factor una sola vez"""
    token = get_token(client, "seller.sales@empresaa.com", "password123")

    product = Product(
        tenant_id=sales_setup["tenant_a"].id,
        sku="SALES-PROD-CF",
        name="Producto Conversión",
        price=Decimal("50.00"),
        cost=Decimal("20.00"),
        stock=Decimal("10"),
        conversion_factor=Decimal("2"),
        tax_rate=Decimal("0.00"),
        product_type=ProductType.stock,
        is_active=True
    )
    db.add(product)
    db.commit()

    sale_data = {
        "point_of_sale_id": sales_setup["pos_a"].id,
        "currency_id": sales_setup["currency"].id,
        "payment_method": "CASH",
        "items": [
            {
                "product_id": product.id,
                "quantity": 3
            }
        ]
    }

    response = client.post(
        "/api/v1/sales/",
        json=sale_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    db.refresh(product)
    assert product.stock == Decimal("4")  # 10 - (3 * 2)


def test_create_sale_service_does_not_deduct_stock(client, db, sales_setup):
    """✅ Servicios no descuentan stock"""
    token = get_token(client, "seller.sales@empresaa.com", "password123")

    service = Product(
        tenant_id=sales_setup["tenant_a"].id,
        sku="SALES-SERVICE-001",
        name="Servicio Test",
        price=Decimal("150.00"),
        cost=Decimal("0.00"),
        stock=Decimal("0"),
        tax_rate=Decimal("0.00"),
        product_type=ProductType.service,
        is_active=True
    )
    db.add(service)
    db.commit()

    sale_data = {
        "point_of_sale_id": sales_setup["pos_a"].id,
        "currency_id": sales_setup["currency"].id,
        "payment_method": "CASH",
        "items": [
            {
                "product_id": service.id,
                "quantity": 2
            }
        ]
    }

    response = client.post(
        "/api/v1/sales/",
        json=sale_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    db.refresh(service)
    assert service.stock == Decimal("0")


# ===== TESTS DE FACTURACIÓN ELECTRÓNICA =====

def test_create_sale_with_cae_when_enabled(client, sales_setup):
    """✅ Facturación electrónica habilitada requiere CAE"""
    token = get_token(client, "admin.sales@empresab.com", "password123")

    sale_data = {
        "point_of_sale_id": sales_setup["pos_b"].id,
        "currency_id": sales_setup["currency"].id,
        "payment_method": "CASH",
        "invoice_type": "B",
        "cae": "71234567890123",
        "cae_expiration": (datetime.utcnow() + timedelta(days=10)).isoformat(),
        "items": [
            {
                "product_id": sales_setup["product_b"].id,
                "quantity": 2
            }
        ]
    }

    response = client.post(
        "/api/v1/sales/",
        json=sale_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["cae"] == "71234567890123"
    assert data["invoice_type"] == "B"


def test_create_sale_without_cae_when_disabled(client, sales_setup):
    """✅ Sin facturación electrónica, CAE es opcional"""
    token = get_token(client, "seller.sales@empresaa.com", "password123")

    sale_data = {
        "point_of_sale_id": sales_setup["pos_a"].id,
        "currency_id": sales_setup["currency"].id,
        "payment_method": "CARD",
        "items": [
            {
                "product_id": sales_setup["product_a"].id,
                "quantity": 1
            }
        ]
    }

    response = client.post(
        "/api/v1/sales/",
        json=sale_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["cae"] is None
    assert data["invoice_type"] is None


# ===== TESTS DE CONSULTA =====

def test_get_sale_by_id_success(client, db, sales_setup):
    """✅ Obtener venta por ID"""
    token = get_token(client, "seller.sales@empresaa.com", "password123")

    # Crear una venta directamente en DB
    sale = Sale(
        tenant_id=sales_setup["tenant_a"].id,
        user_id=sales_setup["user_seller_a"].id,
        point_of_sale_id=sales_setup["pos_a"].id,
        currency_id=sales_setup["currency"].id,
        payment_method="CASH",
        subtotal=Decimal("100"),
        tax_amount=Decimal("21"),
        total=Decimal("121"),
        status="completed",
        invoice_number="00000001"
    )
    db.add(sale)
    db.commit()

    response = client.get(
        f"/api/v1/sales/{sale.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["id"] == sale.id


def test_get_sale_from_other_tenant_blocked(client, db, sales_setup):
    """❌ Seguridad: No puede ver ventas de otro tenant"""
    token_a = get_token(client, "seller.sales@empresaa.com", "password123")

    # Crear venta del Tenant B
    sale_b = Sale(
        tenant_id=sales_setup["tenant_b"].id,
        user_id=sales_setup["user_admin_b"].id,
        point_of_sale_id=sales_setup["pos_b"].id,
        currency_id=sales_setup["currency"].id,
        payment_method="CASH",
        subtotal=Decimal("100"),
        tax_amount=Decimal("21"),
        total=Decimal("121"),
        status="completed",
        invoice_number="00000001"
    )
    db.add(sale_b)
    db.commit()

    # Usuario de Tenant A intenta ver venta de Tenant B
    response = client.get(
        f"/api/v1/sales/{sale_b.id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )

    assert response.status_code == 404


# ===== TESTS DE CANCELACIÓN =====

def test_cancel_sale_success(client, db, sales_setup):
    """✅ Cancelar venta y revertir stock"""
    token = get_token(client, "seller.sales@empresaa.com", "password123")

    # Stock inicial
    product = db.query(Product).filter(
        Product.id == sales_setup["product_a"].id
    ).first()
    initial_stock = product.stock

    # Crear venta con item
    sale = Sale(
        tenant_id=sales_setup["tenant_a"].id,
        user_id=sales_setup["user_seller_a"].id,
        point_of_sale_id=sales_setup["pos_a"].id,
        currency_id=sales_setup["currency"].id,
        payment_method="CASH",
        subtotal=Decimal("500"),
        tax_amount=Decimal("105"),
        total=Decimal("605"),
        status="completed",
        invoice_number="00000002"
    )
    db.add(sale)
    db.flush()

    # Agregar item
    detail = SaleDetail(
        sale_id=sale.id,
        product_id=sales_setup["product_a"].id,
        quantity=Decimal("5"),
        unit_price=Decimal("100"),
        tax_rate=Decimal("21"),
        subtotal=Decimal("500"),
        tax_amount=Decimal("105"),
        total=Decimal("605")
    )
    db.add(detail)

    # Descontar stock
    product.stock -= Decimal("5")
    db.commit()

    # Verificar stock descontado
    db.refresh(product)
    assert product.stock == initial_stock - Decimal("5")

    # Cancelar venta
    response = client.post(
        f"/api/v1/sales/{sale.id}/cancel",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

    # Verificar stock restaurado
    db.refresh(product)
    assert product.stock == initial_stock


def test_cancel_sale_kit_restores_component_stock(client, db, sales_setup):
    """✅ Cancelar venta de kit y restaurar stock de componentes"""
    token = get_token(client, "seller.sales@empresaa.com", "password123")

    component_a = Product(
        tenant_id=sales_setup["tenant_a"].id,
        sku="COMP-A",
        name="Componente A",
        price=Decimal("50.00"),
        cost=Decimal("20.00"),
        stock=Decimal("20"),
        conversion_factor=Decimal("2"),
        tax_rate=Decimal("0.00"),
        product_type=ProductType.stock,
        is_active=True
    )
    component_b = Product(
        tenant_id=sales_setup["tenant_a"].id,
        sku="COMP-B",
        name="Componente B",
        price=Decimal("30.00"),
        cost=Decimal("10.00"),
        stock=Decimal("30"),
        conversion_factor=Decimal("1"),
        tax_rate=Decimal("0.00"),
        product_type=ProductType.stock,
        is_active=True
    )
    kit = Product(
        tenant_id=sales_setup["tenant_a"].id,
        sku="KIT-001",
        name="Kit Test",
        price=Decimal("200.00"),
        cost=Decimal("0.00"),
        stock=Decimal("0"),
        tax_rate=Decimal("0.00"),
        product_type=ProductType.kit,
        is_active=True
    )
    db.add_all([component_a, component_b, kit])
    db.commit()

    kit_component_a = ProductKit(
        kit_product_id=kit.id,
        component_product_id=component_a.id,
        quantity=Decimal("3")
    )
    kit_component_b = ProductKit(
        kit_product_id=kit.id,
        component_product_id=component_b.id,
        quantity=Decimal("1")
    )
    db.add_all([kit_component_a, kit_component_b])
    db.commit()

    initial_stock_a = component_a.stock
    initial_stock_b = component_b.stock

    sale = Sale(
        tenant_id=sales_setup["tenant_a"].id,
        user_id=sales_setup["user_seller_a"].id,
        point_of_sale_id=sales_setup["pos_a"].id,
        currency_id=sales_setup["currency"].id,
        payment_method="CASH",
        subtotal=Decimal("400"),
        tax_amount=Decimal("0"),
        total=Decimal("400"),
        status="completed",
        invoice_number="00000003"
    )
    db.add(sale)
    db.flush()

    detail = SaleDetail(
        sale_id=sale.id,
        product_id=kit.id,
        quantity=Decimal("2"),
        unit_price=Decimal("200"),
        tax_rate=Decimal("0"),
        subtotal=Decimal("400"),
        tax_amount=Decimal("0"),
        total=Decimal("400")
    )
    db.add(detail)

    component_a.stock -= Decimal("3") * Decimal("2") * Decimal("2")
    component_b.stock -= Decimal("1") * Decimal("2") * Decimal("1")
    db.commit()

    db.refresh(component_a)
    db.refresh(component_b)
    assert component_a.stock == initial_stock_a - Decimal("12")
    assert component_b.stock == initial_stock_b - Decimal("2")

    response = client.post(
        f"/api/v1/sales/{sale.id}/cancel",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

    db.refresh(component_a)
    db.refresh(component_b)
    assert component_a.stock == initial_stock_a
    assert component_b.stock == initial_stock_b


def test_cancel_sale_service_does_not_restore_stock(client, db, sales_setup):
    """✅ Cancelar venta de servicio no modifica stock"""
    token = get_token(client, "seller.sales@empresaa.com", "password123")

    service = Product(
        tenant_id=sales_setup["tenant_a"].id,
        sku="SERVICE-001",
        name="Servicio Cancelación",
        price=Decimal("120.00"),
        cost=Decimal("0.00"),
        stock=Decimal("5"),
        conversion_factor=Decimal("3"),
        tax_rate=Decimal("0.00"),
        product_type=ProductType.service,
        is_active=True
    )
    db.add(service)
    db.commit()

    initial_stock = service.stock

    sale = Sale(
        tenant_id=sales_setup["tenant_a"].id,
        user_id=sales_setup["user_seller_a"].id,
        point_of_sale_id=sales_setup["pos_a"].id,
        currency_id=sales_setup["currency"].id,
        payment_method="CASH",
        subtotal=Decimal("120"),
        tax_amount=Decimal("0"),
        total=Decimal("120"),
        status="completed",
        invoice_number="00000004"
    )
    db.add(sale)
    db.flush()

    detail = SaleDetail(
        sale_id=sale.id,
        product_id=service.id,
        quantity=Decimal("1"),
        unit_price=Decimal("120"),
        tax_rate=Decimal("0"),
        subtotal=Decimal("120"),
        tax_amount=Decimal("0"),
        total=Decimal("120")
    )
    db.add(detail)
    db.commit()

    response = client.post(
        f"/api/v1/sales/{sale.id}/cancel",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

    db.refresh(service)
    assert service.stock == initial_stock


def test_pause_and_resume_sale_flow(client, sales_setup):
    """✅ Pausar y recuperar una venta"""
    token = get_token(client, "seller.sales@empresaa.com", "password123")

    sale_data = {
        "client_id": sales_setup["client_a"].id,
        "point_of_sale_id": sales_setup["pos_a"].id,
        "currency_id": sales_setup["currency"].id,
        "payment_method": "CASH",
        "items": [
            {
                "product_id": sales_setup["product_a"].id,
                "quantity": 2
            }
        ]
    }

    response = client.post(
        "/api/v1/sales/",
        json=sale_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    sale_id = response.json()["id"]

    pause_response = client.post(
        f"/api/v1/sales/{sale_id}/pause",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert pause_response.status_code == 200
    assert pause_response.json()["status"] == "on_hold"

    resume_response = client.post(
        f"/api/v1/sales/{sale_id}/resume",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resume_response.status_code == 200
    assert resume_response.json()["status"] == "completed"


# ===== TEST DE LISTADO =====

def test_list_sales_with_filters(client, db, sales_setup):
    """✅ Listar ventas con filtros"""
    token = get_token(client, "seller.sales@empresaa.com", "password123")

    # Crear varias ventas
    for i in range(3):
        sale = Sale(
            tenant_id=sales_setup["tenant_a"].id,
            user_id=sales_setup["user_seller_a"].id,
            point_of_sale_id=sales_setup["pos_a"].id,
            currency_id=sales_setup["currency"].id,
            payment_method="CASH",
            subtotal=Decimal("100"),
            tax_amount=Decimal("21"),
            total=Decimal("121"),
            status="completed",
            invoice_number=f"0000000{i+1}"
        )
        db.add(sale)

    db.commit()

    # Listar ventas
    response = client.get(
        "/api/v1/sales/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    sales = response.json()
    assert len(sales) >= 3
