"""
Tests para movimientos contables manuales.
"""
from datetime import datetime

import pytest

from neos_core.database.models import AccountingLine, AccountingMove, Currency


def test_create_manual_draft_move_balanced(client, db, admin_headers, seed_data):
    currency = Currency(code="ARS", name="Peso Argentino", symbol="$", is_active=True)
    db.add(currency)
    db.commit()

    payload = {
        "currency_id": currency.id,
        "description": "Asiento manual",
        "move_date": "2024-03-10T10:00:00",
        "period_year": 2024,
        "period_month": 3,
        "lines": [
            {"account_code": "111", "description": "Caja", "debit": "100.00", "credit": "0"},
            {"account_code": "211", "description": "Ventas", "debit": "0", "credit": "100.00"}
        ]
    }

    response = client.post(
        "/api/v1/accounting/moves",
        json=payload,
        headers=admin_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "draft"
    assert data["period_year"] == 2024
    assert data["period_month"] == 3
    assert len(data["lines"]) == 2


def test_create_manual_draft_move_unbalanced(client, db, admin_headers, seed_data):
    currency = Currency(code="USD", name="Dólar", symbol="US$", is_active=True)
    db.add(currency)
    db.commit()

    payload = {
        "currency_id": currency.id,
        "description": "Asiento desbalanceado",
        "move_date": "2024-03-11T10:00:00",
        "period_year": 2024,
        "period_month": 3,
        "lines": [
            {"account_code": "111", "description": "Caja", "debit": "100.00", "credit": "0"},
            {"account_code": "211", "description": "Ventas", "debit": "0", "credit": "90.00"}
        ]
    }

    response = client.post(
        "/api/v1/accounting/moves",
        json=payload,
        headers=admin_headers
    )

    assert response.status_code == 400


def test_patch_draft_move_updates_lines(client, db, admin_headers, seed_data):
    currency = Currency(code="EUR", name="Euro", symbol="€", is_active=True)
    db.add(currency)
    db.commit()

    move = AccountingMove(
        tenant_id=seed_data["t1"],
        currency_id=currency.id,
        description="Borrador",
        status="draft",
        move_date=datetime(2024, 3, 1, 9, 0, 0),
        period_year=2024,
        period_month=3
    )
    move.lines.append(
        AccountingLine(account_code="111", description="Caja", debit=50, credit=0)
    )
    move.lines.append(
        AccountingLine(account_code="211", description="Ventas", debit=0, credit=50)
    )
    db.add(move)
    db.commit()

    response = client.patch(
        f"/api/v1/accounting/moves/{move.id}",
        json={
            "description": "Borrador actualizado",
            "lines": [
                {"account_code": "112", "description": "Banco", "debit": "75.00", "credit": "0"},
                {"account_code": "212", "description": "Ventas", "debit": "0", "credit": "75.00"}
            ]
        },
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Borrador actualizado"
    assert len(data["lines"]) == 2
    assert {line["account_code"] for line in data["lines"]} == {"112", "212"}


def test_put_rejects_posted_move(client, db, admin_headers, seed_data):
    currency = Currency(code="GBP", name="Libra", symbol="£", is_active=True)
    db.add(currency)
    db.commit()

    move = AccountingMove(
        tenant_id=seed_data["t1"],
        currency_id=currency.id,
        description="Posteado",
        status="posted",
        move_date=datetime(2024, 3, 1, 9, 0, 0),
        period_year=2024,
        period_month=3,
        posted_at=datetime(2024, 3, 2, 10, 0, 0)
    )
    move.lines.append(
        AccountingLine(account_code="111", description="Caja", debit=20, credit=0)
    )
    move.lines.append(
        AccountingLine(account_code="211", description="Ventas", debit=0, credit=20)
    )
    db.add(move)
    db.commit()

    response = client.put(
        f"/api/v1/accounting/moves/{move.id}",
        json={
            "currency_id": currency.id,
            "description": "Intento de edición",
            "move_date": "2024-03-05T12:00:00",
            "period_year": 2024,
            "period_month": 3,
            "lines": [
                {"account_code": "111", "description": "Caja", "debit": "10.00", "credit": "0"},
                {"account_code": "211", "description": "Ventas", "debit": "0", "credit": "10.00"}
            ]
        },
        headers=admin_headers
    )

    assert response.status_code == 400
