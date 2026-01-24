from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from neos_core.database.models import Expense
from neos_core.schemas.expense_schema import ExpenseCreate
from neos_core.services import accounting_service


def create_expense(db: Session, expense_data: ExpenseCreate, tenant_id: int) -> Expense:
    if expense_data.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="No puedes registrar gastos para otro tenant")

    try:
        with db.begin():
            expense = Expense(
                tenant_id=tenant_id,
                currency_id=expense_data.currency_id,
                description=expense_data.description,
                amount=expense_data.amount,
                suggested_account=expense_data.suggested_account,
            )
            db.add(expense)
            db.flush()

            accounting_service.create_expense_move(db=db, expense=expense)

            db.flush()
            db.refresh(expense)
            return expense
    except SQLAlchemyError:
        db.rollback()
        raise


def get_expense_by_id(db: Session, expense_id: int, tenant_id: int) -> Expense | None:
    return (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.tenant_id == tenant_id)
        .first()
    )


def get_expenses(db: Session, tenant_id: int, skip: int = 0, limit: int = 50):
    return (
        db.query(Expense)
        .filter(Expense.tenant_id == tenant_id)
        .order_by(Expense.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
