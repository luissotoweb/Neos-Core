from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from neos_core.database.models import Purchase
from neos_core.schemas.purchase_schema import PurchaseCreate
from neos_core.services import accounting_service


def create_purchase(db: Session, purchase_data: PurchaseCreate, tenant_id: int) -> Purchase:
    if purchase_data.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="No puedes registrar compras para otro tenant")

    try:
        with db.begin():
            purchase = Purchase(
                tenant_id=tenant_id,
                currency_id=purchase_data.currency_id,
                description=purchase_data.description,
                amount=purchase_data.amount,
                supplier_name=purchase_data.supplier_name,
                suggested_account=purchase_data.suggested_account,
            )
            db.add(purchase)
            db.flush()

            accounting_service.create_purchase_move(db=db, purchase=purchase)

            db.flush()
            db.refresh(purchase)
            return purchase
    except SQLAlchemyError:
        db.rollback()
        raise


def get_purchase_by_id(db: Session, purchase_id: int, tenant_id: int) -> Purchase | None:
    return (
        db.query(Purchase)
        .filter(Purchase.id == purchase_id, Purchase.tenant_id == tenant_id)
        .first()
    )


def get_purchases(db: Session, tenant_id: int, skip: int = 0, limit: int = 50):
    return (
        db.query(Purchase)
        .filter(Purchase.tenant_id == tenant_id)
        .order_by(Purchase.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
