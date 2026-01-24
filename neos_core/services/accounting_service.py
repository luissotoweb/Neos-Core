from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from neos_core.database.models import AccountingLine, AccountingMove, Expense, Purchase, Sale


def create_sale_move(db: Session, sale: Sale) -> AccountingMove:
    move_date = sale.created_at or datetime.utcnow()
    period_year = move_date.year
    period_month = move_date.month

    move = AccountingMove(
        tenant_id=sale.tenant_id,
        sale_id=sale.id,
        currency_id=sale.currency_id,
        description=f"Venta #{sale.id}",
        status="draft",
        move_date=move_date,
        period_year=period_year,
        period_month=period_month
    )

    total = Decimal(sale.total)
    subtotal = Decimal(sale.subtotal)
    tax_amount = Decimal(sale.tax_amount)

    move.lines.append(
        AccountingLine(
            account_code="cash",
            description="Cobro de venta",
            debit=total,
            credit=Decimal("0")
        )
    )
    move.lines.append(
        AccountingLine(
            account_code="sales_revenue",
            description="Ingreso por ventas",
            debit=Decimal("0"),
            credit=subtotal
        )
    )

    if tax_amount > 0:
        move.lines.append(
            AccountingLine(
                account_code="tax_payable",
                description="Impuestos por pagar",
                debit=Decimal("0"),
                credit=tax_amount
            )
        )

    db.add(move)
    db.flush()
    return move


def create_purchase_move(db: Session, purchase: Purchase) -> AccountingMove:
    move_date = purchase.created_at or datetime.utcnow()
    period_year = move_date.year
    period_month = move_date.month

    move = AccountingMove(
        tenant_id=purchase.tenant_id,
        currency_id=purchase.currency_id,
        description=f"Compra #{purchase.id}",
        status="draft",
        move_date=move_date,
        period_year=period_year,
        period_month=period_month
    )

    total = Decimal(purchase.amount)
    expense_account = purchase.suggested_account or "inventory"

    move.lines.append(
        AccountingLine(
            account_code=expense_account,
            description="Registro de compra",
            debit=total,
            credit=Decimal("0")
        )
    )
    move.lines.append(
        AccountingLine(
            account_code="cash",
            description="Pago de compra",
            debit=Decimal("0"),
            credit=total
        )
    )

    db.add(move)
    db.flush()
    return move


def create_expense_move(db: Session, expense: Expense) -> AccountingMove:
    move_date = expense.created_at or datetime.utcnow()
    period_year = move_date.year
    period_month = move_date.month

    move = AccountingMove(
        tenant_id=expense.tenant_id,
        currency_id=expense.currency_id,
        description=f"Gasto #{expense.id}",
        status="draft",
        move_date=move_date,
        period_year=period_year,
        period_month=period_month
    )

    total = Decimal(expense.amount)
    expense_account = expense.suggested_account or "operating_expense"

    move.lines.append(
        AccountingLine(
            account_code=expense_account,
            description="Registro de gasto",
            debit=total,
            credit=Decimal("0")
        )
    )
    move.lines.append(
        AccountingLine(
            account_code="cash",
            description="Pago de gasto",
            debit=Decimal("0"),
            credit=total
        )
    )

    db.add(move)
    db.flush()
    return move
