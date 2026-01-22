from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from neos_core.database.models import AccountingMove


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
