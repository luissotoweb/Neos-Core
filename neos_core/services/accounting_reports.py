from datetime import date, datetime, time
from decimal import Decimal
from typing import Dict, Iterable, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from neos_core.database.models import AccountingLine, AccountingMove


ACCOUNT_CATEGORY_MAP = {
    "cash": "asset",
    "inventory": "asset",
    "tax_payable": "liability",
    "sales_revenue": "revenue",
    "operating_expense": "expense",
}


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _normalize_date_range(
    start_date: Optional[date],
    end_date: Optional[date]
) -> Tuple[Optional[datetime], Optional[datetime]]:
    start_dt = None
    end_dt = None
    if start_date:
        start_dt = datetime.combine(start_date, time.min)
    if end_date:
        end_dt = datetime.combine(end_date, time.max)
    return start_dt, end_dt


def _infer_account_category(account_code: str) -> str:
    if not account_code:
        return "other"

    if account_code in ACCOUNT_CATEGORY_MAP:
        return ACCOUNT_CATEGORY_MAP[account_code]

    if account_code[0].isdigit():
        prefix = account_code[0]
        if prefix == "1":
            return "asset"
        if prefix == "2":
            return "liability"
        if prefix == "3":
            return "equity"
        if prefix == "4":
            return "revenue"
        if prefix in {"5", "6", "7"}:
            return "expense"

    return "other"


def get_accounting_lines_by_period(
    db: Session,
    tenant_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Iterable:
    start_dt, end_dt = _normalize_date_range(start_date, end_date)

    query = (
        db.query(
            AccountingMove.period_year,
            AccountingMove.period_month,
            AccountingLine.account_code,
            func.sum(AccountingLine.debit).label("total_debit"),
            func.sum(AccountingLine.credit).label("total_credit"),
        )
        .join(AccountingLine, AccountingLine.move_id == AccountingMove.id)
        .filter(AccountingMove.tenant_id == tenant_id)
    )

    if start_dt:
        query = query.filter(AccountingMove.move_date >= start_dt)
    if end_dt:
        query = query.filter(AccountingMove.move_date <= end_dt)

    return (
        query.group_by(
            AccountingMove.period_year,
            AccountingMove.period_month,
            AccountingLine.account_code,
        )
        .order_by(
            AccountingMove.period_year,
            AccountingMove.period_month,
            AccountingLine.account_code,
        )
        .all()
    )


def _build_income_statement_periods(rows: Iterable) -> Dict[tuple, Dict]:
    periods: Dict[tuple, Dict] = {}

    for row in rows:
        key = (row.period_year, row.period_month)
        period_entry = periods.setdefault(
            key,
            {
                "period_year": row.period_year,
                "period_month": row.period_month,
                "revenues": Decimal("0"),
                "expenses": Decimal("0"),
                "net_income": Decimal("0"),
                "lines": [],
            },
        )

        debit = _to_decimal(row.total_debit)
        credit = _to_decimal(row.total_credit)
        category = _infer_account_category(row.account_code)
        if category == "revenue":
            balance = credit - debit
            period_entry["revenues"] += balance
        elif category == "expense":
            balance = debit - credit
            period_entry["expenses"] += balance
        else:
            balance = credit - debit

        period_entry["lines"].append(
            {
                "account_code": row.account_code,
                "debit": debit,
                "credit": credit,
                "balance": balance,
                "category": category,
            }
        )

    for period_entry in periods.values():
        period_entry["net_income"] = (
            period_entry["revenues"] - period_entry["expenses"]
        )

    return periods


def get_income_statement(
    db: Session,
    tenant_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[Dict]:
    rows = get_accounting_lines_by_period(
        db=db,
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date,
    )
    periods = _build_income_statement_periods(rows)
    return list(periods.values())


def _build_balance_sheet_periods(rows: Iterable) -> Dict[tuple, Dict]:
    periods: Dict[tuple, Dict] = {}

    for row in rows:
        key = (row.period_year, row.period_month)
        period_entry = periods.setdefault(
            key,
            {
                "period_year": row.period_year,
                "period_month": row.period_month,
                "assets": Decimal("0"),
                "liabilities": Decimal("0"),
                "equity": Decimal("0"),
                "total_liabilities_equity": Decimal("0"),
                "lines": [],
            },
        )

        debit = _to_decimal(row.total_debit)
        credit = _to_decimal(row.total_credit)
        category = _infer_account_category(row.account_code)

        if category == "asset":
            balance = debit - credit
            period_entry["assets"] += balance
        elif category == "liability":
            balance = credit - debit
            period_entry["liabilities"] += balance
        elif category == "equity":
            balance = credit - debit
            period_entry["equity"] += balance
        else:
            balance = debit - credit

        period_entry["lines"].append(
            {
                "account_code": row.account_code,
                "debit": debit,
                "credit": credit,
                "balance": balance,
                "category": category,
            }
        )

    for period_entry in periods.values():
        period_entry["total_liabilities_equity"] = (
            period_entry["liabilities"] + period_entry["equity"]
        )

    return periods


def get_balance_sheet(
    db: Session,
    tenant_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[Dict]:
    rows = get_accounting_lines_by_period(
        db=db,
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date,
    )
    periods = _build_balance_sheet_periods(rows)
    return list(periods.values())
