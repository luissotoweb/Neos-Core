from datetime import date, datetime, time
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from neos_core.database.models import Product, Sale, SaleDetail


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _normalize_date_range(start_date: Optional[date], end_date: Optional[date]):
    start_dt = None
    end_dt = None
    if start_date:
        start_dt = datetime.combine(start_date, time.min)
    if end_date:
        end_dt = datetime.combine(end_date, time.max)
    return start_dt, end_dt


def get_simple_demand_history(
    db: Session,
    tenant_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Dict]:
    start_dt, end_dt = _normalize_date_range(start_date, end_date)

    sale_date = func.date(Sale.created_at)
    query = (
        db.query(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            sale_date.label("sale_date"),
            func.sum(SaleDetail.quantity).label("total_quantity"),
            func.sum(SaleDetail.total).label("total_sales"),
        )
        .join(SaleDetail, SaleDetail.product_id == Product.id)
        .join(Sale, SaleDetail.sale_id == Sale.id)
        .filter(Product.tenant_id == tenant_id, Sale.status == "completed")
    )

    if start_dt:
        query = query.filter(Sale.created_at >= start_dt)
    if end_dt:
        query = query.filter(Sale.created_at <= end_dt)

    rows = (
        query.group_by(Product.id, Product.name, sale_date)
        .order_by(Product.id, sale_date)
        .all()
    )

    aggregated: Dict[int, Dict] = {}
    for row in rows:
        if isinstance(row.sale_date, str):
            row_date = date.fromisoformat(row.sale_date)
        elif isinstance(row.sale_date, datetime):
            row_date = row.sale_date.date()
        else:
            row_date = row.sale_date

        product_entry = aggregated.setdefault(
            row.product_id,
            {
                "product_id": row.product_id,
                "product_name": row.product_name,
                "total_quantity": Decimal("0"),
                "total_sales": Decimal("0"),
                "history": [],
            },
        )

        quantity = _to_decimal(row.total_quantity)
        sales_total = _to_decimal(row.total_sales)

        product_entry["total_quantity"] += quantity
        product_entry["total_sales"] += sales_total
        product_entry["history"].append(
            {
                "date": row_date,
                "total_quantity": quantity,
                "total_sales": sales_total,
            }
        )

    return list(aggregated.values())


def get_basic_anomalies(db: Session, tenant_id: int) -> Dict:
    negative_margin_products = (
        db.query(Product)
        .filter(
            Product.tenant_id == tenant_id,
            Product.is_active.is_(True),
            Product.price < Product.cost,
        )
        .order_by(Product.id)
        .all()
    )

    low_stock_products = (
        db.query(Product)
        .filter(
            Product.tenant_id == tenant_id,
            Product.min_stock.isnot(None),
            Product.stock <= Product.min_stock,
        )
        .order_by(Product.id)
        .all()
    )

    sale_discrepancies = []
    sales = db.query(Sale).filter(Sale.tenant_id == tenant_id).all()
    for sale in sales:
        subtotal = _to_decimal(sale.subtotal)
        tax_amount = _to_decimal(sale.tax_amount)
        total = _to_decimal(sale.total)
        difference = subtotal + tax_amount - total
        if difference.copy_abs() > Decimal("0.01"):
            sale_discrepancies.append(
                {
                    "sale_id": sale.id,
                    "subtotal": subtotal,
                    "tax_amount": tax_amount,
                    "total": total,
                    "difference": difference,
                }
            )

    return {
        "negative_margins": [
            {
                "product_id": product.id,
                "product_name": product.name,
                "cost": _to_decimal(product.cost),
                "price": _to_decimal(product.price),
                "margin": _to_decimal(product.price) - _to_decimal(product.cost),
            }
            for product in negative_margin_products
        ],
        "low_stock": [
            {
                "product_id": product.id,
                "product_name": product.name,
                "stock": _to_decimal(product.stock),
                "min_stock": _to_decimal(product.min_stock),
            }
            for product in low_stock_products
        ],
        "sale_discrepancies": sale_discrepancies,
    }
