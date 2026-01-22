from datetime import date, datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from neos_core.database.models import CashCount, PointOfSale, Sale
from neos_core.schemas.cash_count_schema import CashCountCreate


def _date_range(day: date) -> tuple[datetime, datetime]:
    start = datetime.combine(day, datetime.min.time())
    end = start + timedelta(days=1)
    return start, end


def create_cash_count(
    db: Session,
    tenant_id: int,
    cash_count_data: CashCountCreate
) -> CashCount:
    pos = db.query(PointOfSale).filter_by(
        id=cash_count_data.point_of_sale_id,
        tenant_id=tenant_id
    ).first()
    if not pos:
        raise HTTPException(400, "Punto de venta inválido")

    existing = db.query(CashCount).filter_by(
        tenant_id=tenant_id,
        point_of_sale_id=cash_count_data.point_of_sale_id,
        count_date=cash_count_data.count_date
    ).first()
    if existing:
        raise HTTPException(400, "Ya existe un cierre de caja para esa fecha y POS")

    start, end = _date_range(cash_count_data.count_date)
    recorded_total = (
        db.query(func.coalesce(func.sum(Sale.total), 0))
        .filter(
            Sale.tenant_id == tenant_id,
            Sale.point_of_sale_id == cash_count_data.point_of_sale_id,
            Sale.status == "completed",
            Sale.created_at >= start,
            Sale.created_at < end
        )
        .scalar()
    )

    recorded_amount = Decimal(recorded_total)
    counted_amount = cash_count_data.counted_amount
    difference = counted_amount - recorded_amount

    cash_count = CashCount(
        tenant_id=tenant_id,
        point_of_sale_id=cash_count_data.point_of_sale_id,
        count_date=cash_count_data.count_date,
        counted_amount=counted_amount,
        recorded_amount=recorded_amount,
        difference=difference
    )
    db.add(cash_count)
    db.commit()
    db.refresh(cash_count)
    return cash_count


def get_cash_count(
    db: Session,
    tenant_id: int,
    point_of_sale_id: int,
    count_date: date
) -> CashCount | None:
    return db.query(CashCount).filter_by(
        tenant_id=tenant_id,
        point_of_sale_id=point_of_sale_id,
        count_date=count_date
    ).first()
