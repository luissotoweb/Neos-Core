"""
Tests para cierre de caja (cash count).
"""
from datetime import datetime, date
from decimal import Decimal

import pytest

from neos_core.database.models import Tenant, User, Role, PointOfSale, Currency, Sale
from neos_core.crud.user_crud import get_password_hash


def get_token(client, email: str, password: str):
    response = client.post("/token", data={
        "username": email,
        "password": password
    })
    if response.status_code != 200:
        raise Exception(f"Login failed: {response.json()}")
    return response.json()["access_token"]


@pytest.fixture
def cash_count_setup(db):
    role_seller = db.query(Role).filter(Role.name == "seller").first()
    if not role_seller:
        role_seller = Role(name="seller", description="Vendedor")
        db.add(role_seller)
        db.commit()

    tenant = Tenant(
        name="Empresa CashCount",
        tax_id="20-55555555-9",
        is_active=True,
        electronic_invoicing_enabled=False
    )
    db.add(tenant)
    db.commit()

    user = User(
        email="seller.cashcount@empresa.com",
        hashed_password=get_password_hash("password123"),
        full_name="Caja Tester",
        tenant_id=tenant.id,
        role_id=role_seller.id,
        is_active=True
    )
    db.add(user)
    db.commit()

    currency = Currency(code="ARS", name="Peso Argentino", symbol="$", is_active=True)
    db.add(currency)
    db.commit()

    pos = PointOfSale(
        tenant_id=tenant.id,
        name="Caja Cash Count",
        code="CASH-001",
        is_active=True
    )
    db.add(pos)
    db.commit()

    return {
        "tenant": tenant,
        "user": user,
        "currency": currency,
        "pos": pos
    }


def test_create_cash_count_for_date(client, db, cash_count_setup):
    token = get_token(client, "seller.cashcount@empresa.com", "password123")

    target_date = date(2024, 1, 15)
    sale_a = Sale(
        tenant_id=cash_count_setup["tenant"].id,
        user_id=cash_count_setup["user"].id,
        point_of_sale_id=cash_count_setup["pos"].id,
        currency_id=cash_count_setup["currency"].id,
        payment_method="CASH",
        subtotal=Decimal("100"),
        tax_amount=Decimal("0"),
        total=Decimal("100"),
        status="completed",
        created_at=datetime(2024, 1, 15, 10, 0, 0)
    )
    sale_b = Sale(
        tenant_id=cash_count_setup["tenant"].id,
        user_id=cash_count_setup["user"].id,
        point_of_sale_id=cash_count_setup["pos"].id,
        currency_id=cash_count_setup["currency"].id,
        payment_method="CASH",
        subtotal=Decimal("50"),
        tax_amount=Decimal("0"),
        total=Decimal("50"),
        status="completed",
        created_at=datetime(2024, 1, 15, 12, 0, 0)
    )
    sale_other_date = Sale(
        tenant_id=cash_count_setup["tenant"].id,
        user_id=cash_count_setup["user"].id,
        point_of_sale_id=cash_count_setup["pos"].id,
        currency_id=cash_count_setup["currency"].id,
        payment_method="CASH",
        subtotal=Decimal("30"),
        tax_amount=Decimal("0"),
        total=Decimal("30"),
        status="completed",
        created_at=datetime(2024, 1, 16, 9, 0, 0)
    )
    db.add_all([sale_a, sale_b, sale_other_date])
    db.commit()

    response = client.post(
        "/api/v1/cash-counts/",
        json={
            "point_of_sale_id": cash_count_setup["pos"].id,
            "count_date": str(target_date),
            "counted_amount": "160.00"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["recorded_amount"] == "150.00"
    assert data["difference"] == "10.00"

    get_response = client.get(
        "/api/v1/cash-counts/",
        params={
            "point_of_sale_id": cash_count_setup["pos"].id,
            "count_date": str(target_date)
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 200
    assert get_response.json()["id"] == data["id"]
