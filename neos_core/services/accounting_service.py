from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from neos_core.database.models import AccountingLine, AccountingMove, Sale


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
