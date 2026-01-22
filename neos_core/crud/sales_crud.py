from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from neos_core.database.models import (
    Sale, SaleDetail, Product, Tenant, Client, PointOfSale, Currency
)
from neos_core.schemas.sales_schema import SaleCreate, SaleFilters
from neos_core.services import accounting_service


def create_sale(db: Session, tenant_id: int, user_id: int, sale_data: SaleCreate) -> Sale:
    try:
        with db.begin():

            tenant = db.query(Tenant).filter_by(id=tenant_id, is_active=True).first()
            if not tenant:
                raise HTTPException(403, "Tenant inválido o inactivo")

            pos = db.query(PointOfSale).filter_by(
                id=sale_data.point_of_sale_id,
                tenant_id=tenant_id
            ).first()
            if not pos:
                raise HTTPException(400, "Punto de venta inválido")

            if sale_data.client_id:
                client = db.query(Client).filter_by(
                    id=sale_data.client_id,
                    tenant_id=tenant_id
                ).first()
                if not client:
                    raise HTTPException(400, "Cliente inválido")

            currency = db.query(Currency).filter_by(id=sale_data.currency_id).first()
            if not currency:
                raise HTTPException(400, "Moneda inválida")

            sale = Sale(
                tenant_id=tenant_id,
                user_id=user_id,
                client_id=sale_data.client_id,
                point_of_sale_id=sale_data.point_of_sale_id,
                currency_id=sale_data.currency_id,
                payment_method=sale_data.payment_method,
                status="completed"
            )
            db.add(sale)
            db.flush()

            subtotal = Decimal("0")
            tax_total = Decimal("0")

            for item in sale_data.items:

                product = (
                    db.query(Product)
                    .filter_by(id=item.product_id, tenant_id=tenant_id)
                    .with_for_update()
                    .first()
                )

                if not product:
                    raise HTTPException(404, f"Producto {item.product_id} no existe")

                if product.stock < item.quantity:
                    raise HTTPException(400, f"Stock insuficiente para {product.name}")

                unit_price = product.price
                line_subtotal = unit_price * item.quantity
                tax_rate = Decimal("0")
                tax_amount = Decimal("0")
                line_total = line_subtotal + tax_amount

                product.stock -= item.quantity

                detail = SaleDetail(
                    sale_id=sale.id,
                    product_id=product.id,
                    quantity=item.quantity,
                    unit_price=unit_price,
                    tax_rate=tax_rate,
                    subtotal=line_subtotal,
                    tax_amount=tax_amount,
                    total=line_total
                )

                db.add(detail)

                subtotal += line_subtotal
                tax_total += tax_amount

            sale.subtotal = subtotal
            sale.tax_amount = tax_total
            sale.total = subtotal + tax_total

            accounting_service.create_sale_move(db=db, sale=sale)

            db.flush()
            db.refresh(sale)
            return sale

    except SQLAlchemyError:
        db.rollback()
        raise


def get_sale_by_id(db: Session, sale_id: int, tenant_id: int) -> Sale | None:
    return (
        db.query(Sale)
        .options(joinedload(Sale.items))
        .filter(Sale.id == sale_id, Sale.tenant_id == tenant_id)
        .first()
    )


def get_sales(db: Session, tenant_id: int, filters: SaleFilters):
    q = db.query(Sale).filter(Sale.tenant_id == tenant_id)

    if filters.client_id:
        q = q.filter(Sale.client_id == filters.client_id)
    if filters.point_of_sale_id:
        q = q.filter(Sale.point_of_sale_id == filters.point_of_sale_id)
    if filters.payment_method:
        q = q.filter(Sale.payment_method == filters.payment_method)
    if filters.status:
        q = q.filter(Sale.status == filters.status)

    return q.order_by(Sale.created_at.desc()).offset(filters.skip).limit(filters.limit).all()


def cancel_sale(db: Session, sale_id: int, tenant_id: int, user_id: int) -> Sale:
    with db.begin():
        sale = (
            db.query(Sale)
            .options(joinedload(Sale.items))
            .filter(Sale.id == sale_id, Sale.tenant_id == tenant_id)
            .with_for_update()
            .first()
        )

        if not sale:
            raise HTTPException(404, "Venta no encontrada")

        if sale.status != "completed":
            raise HTTPException(400, "Solo se pueden cancelar ventas completadas")

        for item in sale.items:
            product = db.query(Product).filter_by(id=item.product_id).with_for_update().first()
            product.stock += item.quantity

        sale.status = "cancelled"
        db.flush()
        db.refresh(sale)
        return sale
