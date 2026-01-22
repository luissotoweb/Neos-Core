# neos_core/crud/product_crud.py
"""
CRUD operations para productos (inventario)
"""
from sqlalchemy.orm import Session
from sqlalchemy import case, func, or_
from typing import List, Optional
from fastapi import HTTPException, status

from neos_core.database.models import Product, ProductKit, ProductType
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

    data = product.model_dump()
    kit_components = data.pop("kit_components", None)

    if data.get("is_service"):
        data["product_type"] = ProductType.service
    data["is_service"] = data.get("product_type") == ProductType.service

    if kit_components and data.get("product_type") != ProductType.kit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo puedes definir componentes si el producto es un kit"
        )

    if data.get("product_type") == ProductType.kit and not kit_components:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un kit debe incluir componentes"
        )

    if kit_components:
        component_ids = {component["component_product_id"] for component in kit_components}
        components = db.query(Product).filter(
            Product.id.in_(component_ids),
            Product.tenant_id == product.tenant_id
        ).all()
        if len(components) != len(component_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hay componentes de kit inválidos para este tenant"
            )

    db_product = Product(**data)
    db.add(db_product)

    if kit_components:
        db.flush()
        for component in kit_components:
            db.add(ProductKit(
                kit_product_id=db_product.id,
                component_product_id=component["component_product_id"],
                quantity=component["quantity"]
            ))

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
    kit_components = update_data.pop("kit_components", None)

    if update_data.get("is_service"):
        update_data["product_type"] = ProductType.service

    if "product_type" in update_data:
        update_data["is_service"] = update_data["product_type"] == ProductType.service

    target_type = update_data.get("product_type", db_product.product_type)

    if kit_components is not None and target_type != ProductType.kit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo puedes definir componentes si el producto es un kit"
        )

    if target_type == ProductType.kit and kit_components is not None:
        if not kit_components:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un kit debe incluir componentes"
            )
        component_ids = {component["component_product_id"] for component in kit_components}
        if db_product.id in component_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un kit no puede incluirse a sí mismo como componente"
            )
        components = db.query(Product).filter(
            Product.id.in_(component_ids),
            Product.tenant_id == db_product.tenant_id
        ).all()
        if len(components) != len(component_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hay componentes de kit inválidos para este tenant"
            )

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

    if target_type != ProductType.kit:
        db.query(ProductKit).filter(
            ProductKit.kit_product_id == db_product.id
        ).delete()
    elif kit_components is not None:
        db.query(ProductKit).filter(
            ProductKit.kit_product_id == db_product.id
        ).delete()
        for component in kit_components:
            db.add(ProductKit(
                kit_product_id=db_product.id,
                component_product_id=component["component_product_id"],
                quantity=component["quantity"]
            ))

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
        Product.product_type == ProductType.stock,
        Product.stock <= Product.min_stock
    ).all()


def search_products(
        db: Session,
        tenant_id: int,
        query: str,
        skip: int = 0,
        limit: int = 100
) -> List[Product]:
    """
    Busca productos por relevancia dentro del tenant.
    Estrategia: pg_trgm (PostgreSQL) con pesos y fallback ILIKE.
    """
    search_term = f"%{query.strip()}%"
    base_query = db.query(Product).filter(Product.tenant_id == tenant_id)
    text_filter = or_(
        Product.name.ilike(search_term),
        Product.sku.ilike(search_term),
        Product.barcode.ilike(search_term),
        Product.description.ilike(search_term)
    )

    if db.bind and db.bind.dialect.name == "postgresql":
        similarity = func.similarity
        rank = (
            func.coalesce(similarity(Product.name, query), 0) * 0.5
            + func.coalesce(similarity(Product.sku, query), 0) * 0.3
            + func.coalesce(similarity(Product.barcode, query), 0) * 0.1
            + func.coalesce(similarity(Product.description, query), 0) * 0.1
        ).label("rank")
        trigram_filter = or_(
            similarity(Product.name, query) > 0.1,
            similarity(Product.sku, query) > 0.1,
            similarity(Product.barcode, query) > 0.1,
            similarity(Product.description, query) > 0.1
        )
        results = (
            base_query
            .filter(or_(text_filter, trigram_filter))
            .add_columns(rank)
            .order_by(rank.desc(), Product.name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [row[0] for row in results]

    rank = case(
        (Product.name.ilike(search_term), 4),
        (Product.sku.ilike(search_term), 3),
        (Product.barcode.ilike(search_term), 2),
        (Product.description.ilike(search_term), 1),
        else_=0
    ).label("rank")
    results = (
        base_query
        .filter(text_filter)
        .add_columns(rank)
        .order_by(rank.desc(), Product.name.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [row[0] for row in results]
