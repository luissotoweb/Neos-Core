from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from neos_core.database.models import AccountingLine, AccountingMove, Currency
from neos_core.schemas.accounting_schema import (
    AccountingLineCreate,
    AccountingMoveCreate,
    AccountingMovePatch,
    AccountingMoveUpdate
)


def list_draft_moves(
    db: Session,
    tenant_id: int,
    period_year: int | None = None,
    period_month: int | None = None,
    skip: int = 0,
    limit: int = 50
):
    query = (
        db.query(AccountingMove)
        .options(joinedload(AccountingMove.lines))
        .filter(AccountingMove.tenant_id == tenant_id, AccountingMove.status == "draft")
    )

    if period_year:
        query = query.filter(AccountingMove.period_year == period_year)
    if period_month:
        query = query.filter(AccountingMove.period_month == period_month)

    return (
        query.order_by(AccountingMove.move_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def _get_line_amount(line, key: str) -> Decimal:
    if isinstance(line, dict):
        return Decimal(line[key])
    return Decimal(getattr(line, key))


def _validate_balance(lines: list[AccountingLine | AccountingLineCreate | dict]):
    total_debit = Decimal("0")
    total_credit = Decimal("0")
    for line in lines:
        total_debit += _get_line_amount(line, "debit")
        total_credit += _get_line_amount(line, "credit")
    if total_debit != total_credit:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "El movimiento está desbalanceado (debe y haber deben ser iguales)."
        )


def create_manual_move(db: Session, tenant_id: int, move_data: AccountingMoveCreate) -> AccountingMove:
    _validate_balance(move_data.lines)

    currency = db.query(Currency).filter_by(id=move_data.currency_id).first()
    if not currency:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Moneda inválida")

    with db.begin():
        move = AccountingMove(
            tenant_id=tenant_id,
            sale_id=None,
            currency_id=move_data.currency_id,
            description=move_data.description,
            status="draft",
            move_date=move_data.move_date,
            period_year=move_data.period_year,
            period_month=move_data.period_month,
            posted_at=None
        )
        for line in move_data.lines:
            move.lines.append(
                AccountingLine(
                    account_code=line.account_code,
                    description=line.description,
                    debit=line.debit,
                    credit=line.credit
                )
            )
        db.add(move)
        db.flush()
        db.refresh(move)
        return move


def update_draft_move(
    db: Session,
    tenant_id: int,
    move_id: int,
    move_data: AccountingMoveUpdate | AccountingMovePatch,
    *,
    partial: bool = False
) -> AccountingMove:
    update_data = move_data.model_dump(exclude_unset=partial)

    if "lines" in update_data:
        if not update_data["lines"]:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "El movimiento debe tener al menos una línea."
            )
        _validate_balance(update_data["lines"])

    with db.begin():
        move = (
            db.query(AccountingMove)
            .options(joinedload(AccountingMove.lines))
            .filter(AccountingMove.id == move_id, AccountingMove.tenant_id == tenant_id)
            .with_for_update()
            .first()
        )

        if not move:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Movimiento contable no encontrado")

        if move.status != "draft":
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Solo se pueden editar movimientos en borrador."
            )

        if "currency_id" in update_data:
            currency = db.query(Currency).filter_by(id=update_data["currency_id"]).first()
            if not currency:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Moneda inválida")
            move.currency_id = update_data["currency_id"]

        if "description" in update_data:
            move.description = update_data["description"]

        if "move_date" in update_data:
            move.move_date = update_data["move_date"]

        if "period_year" in update_data:
            move.period_year = update_data["period_year"]

        if "period_month" in update_data:
            move.period_month = update_data["period_month"]

        if "lines" in update_data:
            move.lines.clear()
            for line in update_data["lines"]:
                move.lines.append(
                    AccountingLine(
                        account_code=line["account_code"],
                        description=line.get("description"),
                        debit=line["debit"],
                        credit=line["credit"]
                    )
                )

        db.flush()
        db.refresh(move)
        return move


def close_period(db: Session, tenant_id: int, period_year: int, period_month: int) -> int:
    with db.begin():
        moves = (
            db.query(AccountingMove)
            .filter(
                AccountingMove.tenant_id == tenant_id,
                AccountingMove.period_year == period_year,
                AccountingMove.period_month == period_month,
                AccountingMove.status == "draft"
            )
            .with_for_update()
            .all()
        )

        closed_at = datetime.utcnow()
        for move in moves:
            move.status = "posted"
            move.posted_at = closed_at

        return len(moves)
