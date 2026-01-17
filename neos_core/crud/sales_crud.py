"""
CRUD Operations para el módulo de ventas
Incluye validaciones de seguridad, transacciones atómicas y control de stock
"""
from decimal import Decimal
from typing import Optional, List
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from neos_core.database.models import Sale, SaleDetail, Product, Tenant, Client, PointOfSale, Currency
from neos_core.schemas.sales_schema import SaleCreate, SaleFilters


def create_sale(
    db: Session,
    tenant_id: int,
    user_id: int,
    sale_data: SaleCreate
) -> Sale:
    """
    Crea una venta completa con sus items.
    Operación ATÓMICA: Si falla algo, se hace rollback de todo.

    Validaciones:
    1. Verifica que el cliente pertenezca al tenant (si aplica)
    2. Verifica que el POS pertenezca al tenant
    3. Verifica stock suficiente para cada producto
    4. Verifica que los productos pertenezcan al tenant
    5. Valida configuración de facturación electrónica
    """

    # ===== VALIDACIÓN 1: Obtener configuración del Tenant =====
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant or not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant inactivo o inexistente"
        )

    # ===== VALIDACIÓN 2: Cliente (si se proporciona) =====
    if sale_data.client_id:
        client = db.query(Client).filter(
            Client.id == sale_data.client_id,
            Client.tenant_id == tenant_id
        ).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado o no pertenece a tu empresa"
            )

    # ===== VALIDACIÓN 3: Punto de Venta =====
    pos = db.query(PointOfSale).filter(
        PointOfSale.id == sale_data.point_of_sale_id,
        PointOfSale.tenant_id == tenant_id
    ).first()
    if not pos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Punto de venta no encontrado"
        )

    # ===== VALIDACIÓN 4: Moneda =====
    currency = db.query(Currency).filter(Currency.id == sale_data.currency_id).first()
    if not currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Moneda no válida"
        )

    # ===== VALIDACIÓN 5: Facturación Electrónica =====
    if tenant.electronic_invoicing_enabled:
        # Si está habilitada, los campos CAE son obligatorios
        if not all([sale_data.invoice_type, sale_data.cae, sale_data.cae_expiration]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Facturación electrónica habilitada: se requieren invoice_type, CAE y fecha de expiración"
            )
    else:
        # Si está deshabilitada, ignoramos los campos CAE aunque vengan
        sale_data.invoice_type = None
        sale_data.cae = None
        sale_data.cae_expiration = None

    # ===== INICIO DE TRANSACCIÓN =====
    try:
        # Crear venta principal (sin totales aún)
        sale = Sale(
            tenant_id=tenant_id,
            user_id=user_id,
            client_id=sale_data.client_id,
            point_of_sale_id=sale_data.point_of_sale_id,
            currency_id=sale_data.currency_id,
            exchange_rate=sale_data.exchange_rate,
            payment_method=sale_data.payment_method,
            notes=sale_data.notes,
            invoice_type=sale_data.invoice_type,
            cae=sale_data.cae,
            cae_expiration=sale_data.cae_expiration,
            status="pending"
        )

        db.add(sale)
        db.flush()  # Obtiene sale.id sin hacer commit

        # ===== VALIDACIÓN Y CREACIÓN DE ITEMS =====
        subtotal_total = Decimal("0")
        tax_total = Decimal("0")

        for item in sale_data.items:
            # Verificar que el producto existe y pertenece al tenant
            product = db.query(Product).filter(
                Product.id == item.product_id,
                Product.tenant_id == tenant_id
            ).first()

            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Producto {item.product_id} no encontrado o no pertenece a tu empresa"
                )

            # Verificar stock suficiente
            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuficiente para {product.name}. Disponible: {product.stock}, Solicitado: {item.quantity}"
                )

            # Calcular montos del item
            item_subtotal = item.quantity * product.price
            item_tax = item_subtotal * (product.tax_rate / Decimal("100"))
            item_total = item_subtotal + item_tax

            # Crear detalle de venta
            detail = SaleDetail(
                sale_id=sale.id,
                product_id=product.id,
                quantity=item.quantity,
                unit_price=product.price,
                tax_rate=product.tax_rate,
                subtotal=item_subtotal,
                tax_amount=item_tax,
                total=item_total
            )

            db.add(detail)

            # Descontar stock (CRÍTICO: Solo si todo sale bien)
            product.stock -= item.quantity

            # Acumular totales
            subtotal_total += item_subtotal
            tax_total += item_tax

        # ===== ACTUALIZAR TOTALES DE LA VENTA =====
        sale.subtotal = subtotal_total
        sale.tax_amount = tax_total
        sale.total = subtotal_total + tax_total
        sale.status = "completed"

        # ===== GENERAR NÚMERO DE FACTURA (Lógica simplificada) =====
        # En producción, esto debe ser más sofisticado (numeración por POS, etc.)
        last_sale = db.query(Sale).filter(
            Sale.tenant_id == tenant_id,
            Sale.point_of_sale_id == sale_data.point_of_sale_id
        ).order_by(Sale.id.desc()).first()

        next_number = 1 if not last_sale else (int(last_sale.invoice_number or "0") + 1)
        sale.invoice_number = str(next_number).zfill(8)  # Ej: 00000001

        # ===== COMMIT FINAL =====
        db.commit()
        db.refresh(sale)

        return sale

    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad: {str(e.orig)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al crear venta: {str(e)}"
        )


def get_sale_by_id(db: Session, sale_id: int, tenant_id: int) -> Optional[Sale]:
    """
    Obtiene una venta por ID con aislamiento de tenant.
    Incluye los items relacionados (joinedload para evitar N+1 queries).
    """
    sale = db.query(Sale).options(
        joinedload(Sale.items).joinedload(SaleDetail.product)
    ).filter(
        Sale.id == sale_id,
        Sale.tenant_id == tenant_id
    ).first()

    return sale


def get_sales(
    db: Session,
    tenant_id: int,
    filters: SaleFilters
) -> List[Sale]:
    """
    Lista ventas con filtros opcionales.
    Aislamiento por tenant.
    """
    query = db.query(Sale).filter(Sale.tenant_id == tenant_id)

    # Aplicar filtros
    if filters.client_id:
        query = query.filter(Sale.client_id == filters.client_id)

    if filters.point_of_sale_id:
        query = query.filter(Sale.point_of_sale_id == filters.point_of_sale_id)

    if filters.date_from:
        query = query.filter(Sale.created_at >= filters.date_from)

    if filters.date_to:
        query = query.filter(Sale.created_at <= filters.date_to)

    if filters.payment_method:
        query = query.filter(Sale.payment_method == filters.payment_method.upper())

    if filters.status:
        query = query.filter(Sale.status == filters.status)

    # Ordenar por fecha descendente (más recientes primero)
    query = query.order_by(Sale.created_at.desc())

    # Paginación
    sales = query.offset(filters.skip).limit(filters.limit).all()

    return sales


def cancel_sale(db: Session, sale_id: int, tenant_id: int, user_id: int) -> Sale:
    """
    Cancela una venta y revierte el stock.
    Solo puede cancelar si está en estado "completed".
    """
    sale = get_sale_by_id(db, sale_id, tenant_id)

    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada"
        )

    if sale.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden cancelar ventas completadas"
        )

    try:
        # Revertir stock de cada item
        for item in sale.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock += item.quantity

        # Cambiar estado
        sale.status = "cancelled"
        sale.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(sale)

        return sale

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cancelar venta: {str(e)}"
        )