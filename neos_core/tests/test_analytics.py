"""
Tests para endpoints de analíticas básicas.
"""
from datetime import datetime
from decimal import Decimal

import pytest

from neos_core.database import models


@pytest.fixture
def analytics_setup(db, seed_data):
    currency = models.Currency(code="USD", name="Dólar", symbol="$", is_active=True)
    db.add(currency)
    db.commit()

    pos = models.PointOfSale(
        tenant_id=seed_data["t1"],
        name="Caja Analytics",
        code="AN-001",
        is_active=True
    )
    db.add(pos)
    db.commit()

    product_ok = models.Product(
        tenant_id=seed_data["t1"],
        sku="ANA-OK",
        name="Producto OK",
        price=Decimal("100.00"),
        cost=Decimal("50.00"),
        stock=Decimal("20"),
        min_stock=Decimal("5"),
        tax_rate=Decimal("21.00"),
        is_active=True
    )
    product_negative = models.Product(
        tenant_id=seed_data["t1"],
        sku="ANA-NEG",
        name="Producto Margen Negativo",
        price=Decimal("80.00"),
        cost=Decimal("100.00"),
        stock=Decimal("10"),
        min_stock=Decimal("2"),
        tax_rate=Decimal("0"),
        is_active=True
    )
    product_low_stock = models.Product(
        tenant_id=seed_data["t1"],
        sku="ANA-LOW",
        name="Producto Stock Bajo",
        price=Decimal("50.00"),
        cost=Decimal("30.00"),
        stock=Decimal("1"),
        min_stock=Decimal("5"),
        tax_rate=Decimal("0"),
        is_active=True
    )
    db.add_all([product_ok, product_negative, product_low_stock])
    db.commit()

    sale_one = models.Sale(
        tenant_id=seed_data["t1"],
        user_id=2,
        point_of_sale_id=pos.id,
        currency_id=currency.id,
        subtotal=Decimal("300.00"),
        tax_amount=Decimal("63.00"),
        total=Decimal("363.00"),
        payment_method="CASH",
        status="completed",
        created_at=datetime(2024, 1, 10)
    )
    sale_one.items = [
        models.SaleDetail(
            product_id=product_ok.id,
            quantity=Decimal("3"),
            unit_price=Decimal("100.00"),
            tax_rate=Decimal("21.00"),
            subtotal=Decimal("300.00"),
            tax_amount=Decimal("63.00"),
            total=Decimal("363.00")
        )
    ]

    sale_two = models.Sale(
        tenant_id=seed_data["t1"],
        user_id=2,
        point_of_sale_id=pos.id,
        currency_id=currency.id,
        subtotal=Decimal("200.00"),
        tax_amount=Decimal("42.00"),
        total=Decimal("242.00"),
        payment_method="CARD",
        status="completed",
        created_at=datetime(2024, 1, 11)
    )
    sale_two.items = [
        models.SaleDetail(
            product_id=product_ok.id,
            quantity=Decimal("2"),
            unit_price=Decimal("100.00"),
            tax_rate=Decimal("21.00"),
            subtotal=Decimal("200.00"),
            tax_amount=Decimal("42.00"),
            total=Decimal("242.00")
        )
    ]

    sale_discrepancy = models.Sale(
        tenant_id=seed_data["t1"],
        user_id=2,
        point_of_sale_id=pos.id,
        currency_id=currency.id,
        subtotal=Decimal("100.00"),
        tax_amount=Decimal("21.00"),
        total=Decimal("150.00"),
        payment_method="CASH",
        status="completed",
        created_at=datetime(2024, 1, 12)
    )
    sale_discrepancy.items = [
        models.SaleDetail(
            product_id=product_low_stock.id,
            quantity=Decimal("1"),
            unit_price=Decimal("100.00"),
            tax_rate=Decimal("21.00"),
            subtotal=Decimal("100.00"),
            tax_amount=Decimal("21.00"),
            total=Decimal("121.00")
        )
    ]

    db.add_all([sale_one, sale_two, sale_discrepancy])
    db.commit()

    return {
        "product_ok": product_ok,
        "product_negative": product_negative,
        "product_low_stock": product_low_stock,
        "sale_discrepancy": sale_discrepancy,
    }


def test_simple_demand_endpoint(client, admin_headers, analytics_setup):
    response = client.get(
        "/api/v1/analytics/demand-simple",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    product_entry = next(
        item for item in data if item["product_id"] == analytics_setup["product_ok"].id
    )
    assert float(product_entry["total_quantity"]) == 5.0
    assert float(product_entry["total_sales"]) == 605.0
    assert len(product_entry["history"]) == 2


def test_basic_anomalies_endpoint(client, admin_headers, analytics_setup):
    response = client.get(
        "/api/v1/analytics/anomalies",
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    negative_ids = {item["product_id"] for item in data["negative_margins"]}
    low_stock_ids = {item["product_id"] for item in data["low_stock"]}
    discrepancy_ids = {item["sale_id"] for item in data["sale_discrepancies"]}

    assert analytics_setup["product_negative"].id in negative_ids
    assert analytics_setup["product_low_stock"].id in low_stock_ids
    assert analytics_setup["sale_discrepancy"].id in discrepancy_ids
