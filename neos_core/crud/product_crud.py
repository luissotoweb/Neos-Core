# neos_core/crud/product_crud.py
"""
CRUD operations para productos (inventario)
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status

from neos_core.database.models import Product
from neos_core.schemas.product_schema import ProductCreate, ProductUpdate


def _validate_unit_conversion(
        purchase_unit: str,
        sale_unit: str,
        conversion_factor
) -> None:
    if not purchase_unit or not purchase_unit.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La unidad de compra es obligatoria"
        )

    if not sale_unit or not sale_unit.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La unidad de venta es obligatoria"
        )

    if conversion_factor is None or conversion_factor <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El factor de conversión debe ser mayor a 0"
        )


def create_product(db: Session, product: ProductCreate) -> Product:
    """Crea un nuevo producto"""
    _validate_unit_conversion(
        purchase_unit=product.purchase_unit,
        sale_unit=product.sale_unit,
        conversion_factor=product.conversion_factor
    )
    # Verificar que no exista un producto con el mismo SKU en el tenant
    existing = db.query(Product).filter(
        Product.sku == product.sku,
        Product.tenant_id == product.tenant_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un producto con el SKU '{product.sku}' en tu empresa"
        )

    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_products_by_tenant(
        db: Session,
        tenant_id: int,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
) -> List[Product]:
    """
    Lista productos de un tenant con paginación
    Opcionalmente filtra por estado activo/inactivo
    """
    query = db.query(Product).filter(Product.tenant_id == tenant_id)

    if is_active is not None:
        query = query.filter(Product.is_active == is_active)

    return query.offset(skip).limit(limit).all()


def get_product_by_id(db: Session, product_id: int, tenant_id: int) -> Optional[Product]:
    """
    Obtiene un producto por ID con aislamiento de tenant
    IMPORTANTE: Siempre filtra por tenant_id para seguridad
    """
    return db.query(Product).filter(
        Product.id == product_id,
        Product.tenant_id == tenant_id
    ).first()


def get_product_by_sku(db: Session, sku: str, tenant_id: int) -> Optional[Product]:
    """Busca un producto por SKU dentro del tenant"""
    return db.query(Product).filter(
        Product.sku == sku,
        Product.tenant_id == tenant_id
    ).first()


def get_product_by_barcode(db: Session, barcode: str, tenant_id: int) -> Optional[Product]:
    """Busca un producto por código de barras dentro del tenant"""
    return db.query(Product).filter(
        Product.barcode == barcode,
        Product.tenant_id == tenant_id
    ).first()


def update_product(
        db: Session,
        product_id: int,
        tenant_id: int,
        product_update: ProductUpdate
) -> Product:
    """
    Actualiza un producto existente
    Solo actualiza los campos que vienen en el request (no-None)
    """
    db_product = get_product_by_id(db, product_id, tenant_id)

    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    # Actualizar solo los campos que vinieron en el request
    update_data = product_update.model_dump(exclude_unset=True)

    if {
        "purchase_unit",
        "sale_unit",
        "conversion_factor"
    }.intersection(update_data):
        _validate_unit_conversion(
            purchase_unit=update_data.get("purchase_unit", db_product.purchase_unit),
            sale_unit=update_data.get("sale_unit", db_product.sale_unit),
            conversion_factor=update_data.get("conversion_factor", db_product.conversion_factor)
        )

    for field, value in update_data.items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int, tenant_id: int) -> bool:
    """
    Elimina (soft delete) un producto marcándolo como inactivo
    Para eliminación física, cambiar a db.delete(db_product)
    """
    db_product = get_product_by_id(db, product_id, tenant_id)

    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    # Soft delete
    db_product.is_active = False
    db.commit()

    return True


def get_low_stock_products(db: Session, tenant_id: int) -> List[Product]:
    """
    Retorna productos con stock por debajo del mínimo
    Útil para alertas de reposición
    """
    return db.query(Product).filter(
        Product.tenant_id == tenant_id,
        Product.is_active == True,
        Product.is_service == False,  # Los servicios no tienen stock
        Product.stock <= Product.min_stock
    ).all()
