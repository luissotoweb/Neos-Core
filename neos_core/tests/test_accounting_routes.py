from datetime import datetime

from fastapi import status

from neos_core.database import models


def _create_currency(db, code="ARS"):
    currency = models.Currency(code=code, name=code, symbol=code, is_active=True)
    db.add(currency)
    db.commit()
    return currency


def _create_move(
    db,
    *,
    tenant_id,
    currency_id,
    status_value="draft",
    period_year=2024,
    period_month=3,
    move_date=None,
):
    move = models.AccountingMove(
        tenant_id=tenant_id,
        currency_id=currency_id,
        description="Move",
        status=status_value,
        move_date=move_date or datetime(2024, 3, 1, 9, 0, 0),
        period_year=period_year,
        period_month=period_month,
        posted_at=datetime(2024, 3, 2, 10, 0, 0) if status_value == "posted" else None,
    )
    move.lines.append(
        models.AccountingLine(account_code="111", description="Caja", debit=50, credit=0)
    )
    move.lines.append(
        models.AccountingLine(account_code="211", description="Ventas", debit=0, credit=50)
    )
    db.add(move)
    db.commit()
    return move


def test_list_draft_moves_filters_by_period_and_tenant(client, db, admin_headers, seed_data):
    currency = _create_currency(db)

    _create_move(db, tenant_id=seed_data["t1"], currency_id=currency.id, period_month=3)
    _create_move(db, tenant_id=seed_data["t1"], currency_id=currency.id, period_month=4)
    _create_move(db, tenant_id=2, currency_id=currency.id, period_month=3)

    response = client.get(
        "/api/v1/accounting/moves/drafts",
        params={"period_year": 2024, "period_month": 3},
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["tenant_id"] == seed_data["t1"]
    assert data[0]["period_month"] == 3


def test_close_period_posts_only_tenant_drafts(client, db, admin_headers, seed_data):
    currency = _create_currency(db, code="USD")

    _create_move(db, tenant_id=seed_data["t1"], currency_id=currency.id, period_month=5)
    _create_move(db, tenant_id=seed_data["t1"], currency_id=currency.id, period_month=6)
    _create_move(db, tenant_id=2, currency_id=currency.id, period_month=5)

    response = client.post(
        "/api/v1/accounting/periods/close",
        json={"period_year": 2024, "period_month": 5},
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["closed_moves"] == 1

    tenant_one_moves = (
        db.query(models.AccountingMove)
        .filter(models.AccountingMove.tenant_id == seed_data["t1"])
        .all()
    )
    assert {move.status for move in tenant_one_moves} == {"posted", "draft"}

    tenant_two_move = (
        db.query(models.AccountingMove)
        .filter(models.AccountingMove.tenant_id == 2)
        .first()
    )
    assert tenant_two_move.status == "draft"


def test_create_move_validation_errors(client, db, admin_headers, seed_data):
    currency = _create_currency(db, code="EUR")

    response = client.post(
        "/api/v1/accounting/moves",
        json={
            "currency_id": currency.id,
            "description": "Invalid",
            "move_date": "2024-03-10T10:00:00",
            "period_year": 2024,
            "period_month": 3,
            "lines": [
                {"account_code": "111", "description": "Caja", "debit": "100.00", "credit": "0"},
                {"account_code": "211", "description": "Ventas", "debit": "0", "credit": "90.00"},
            ],
        },
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "desbalanceado" in response.json()["detail"]
