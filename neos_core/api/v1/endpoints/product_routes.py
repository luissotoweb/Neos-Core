# neos_core/api/v1/endpoints/product_routes.py
"""
Endpoints para gestión de productos (inventario)
Incluye: CREATE, READ, UPDATE, DELETE y búsquedas especiales
"""
from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from neos_core.database.config import get_db
from neos_core.database.models import User, Product
from neos_core.security.security_deps import get_current_user
from neos_core.schemas.product_schema import (
    Product as ProductSchema,
    ProductCreate,
    ProductUpdate,
    ProductListResponse,
    ProductSemanticSearchResult,
)
from neos_core.crud import product_crud as crud
from neos_core.services.product_semantic_search_service import semantic_search_products

router = APIRouter()


def _validate_unit_conversion(
        purchase_unit: Optional[str],
        sale_unit: Optional[str],
        conversion_factor: Optional[Decimal]
) -> None:
    if purchase_unit is not None and not purchase_unit.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La unidad de compra no puede estar vacía"
        )

    if sale_unit is not None and not sale_unit.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La unidad de venta no puede estar vacía"
        )

    if conversion_factor is not None and conversion_factor <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El factor de conversión debe ser mayor a 0"
        )


# ===== DEPENDENCIA DE PERMISOS =====
def check_product_write_permission(current_user: User = Depends(get_current_user)):
    """
    Verifica permisos para crear/modificar productos
    Roles permitidos: inventory, admin, superadmin
    """
    allowed_roles = ["inventory", "admin", "superadmin"]

    if current_user.role.name not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permiso denegado. Roles permitidos: {', '.join(allowed_roles)}"
        )

    return current_user


# ===== CREATE =====
@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
def create_product(
        product: ProductCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_product_write_permission)
):
    """
    Crea un nuevo producto.

    **Permisos requeridos:** inventory, admin, superadmin

    **Validaciones:**
    - SKU único dentro del tenant
    - Pertenencia al tenant del usuario (excepto superadmin)
    """
    # Seguridad: Un Admin/Inventory no puede crear productos para otro Tenant
    if current_user.role.name != "superadmin" and current_user.tenant_id != product.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes crear productos para otra empresa"
        )

    _validate_unit_conversion(
        purchase_unit=product.purchase_unit,
        sale_unit=product.sale_unit,
        conversion_factor=product.conversion_factor
    )

    return crud.create_product(db=db, product=product)


# ===== READ (LIST) =====
@router.get("/", response_model=List[ProductListResponse])
def list_products(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Lista productos con paginación.

    **Filtros:**
    - is_active: true/false para filtrar por estado

    **Aislamiento:**
    - SuperAdmin ve todos los productos
    - Otros usuarios solo ven productos de su tenant
    """
    # SuperAdmin puede ver todos los productos
    if current_user.role.name == "superadmin":
        query = db.query(Product)

        if is_active is not None:
            query = query.filter(Product.is_active == is_active)

        return query.offset(skip).limit(limit).all()

    # Usuarios normales solo ven productos de su tenant
    return crud.get_products_by_tenant(
        db=db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
        is_active=is_active
    )


# ===== SEARCH =====
@router.get("/search", response_model=List[ProductListResponse])
def search_products(
        query: str = Query(..., min_length=1, description="Texto a buscar"),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Busca productos por relevancia dentro del tenant.
    """
    return crud.search_products(
        db=db,
        tenant_id=current_user.tenant_id,
        query=query,
        skip=skip,
        limit=limit
    )


# ===== SEMANTIC SEARCH =====
@router.get("/search/semantic", response_model=List[ProductSemanticSearchResult])
def semantic_search(
        query: str = Query(..., min_length=1, description="Texto a comparar semánticamente"),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=200),
        tenant_id: Optional[int] = Query(None, gt=0, description="Tenant objetivo (solo superadmin)"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Búsqueda semántica de productos usando embeddings.
    """
    if current_user.role.name == "superadmin":
        if tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="tenant_id es requerido para superadmin",
            )
        target_tenant_id = tenant_id
    else:
        if tenant_id is not None and tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes buscar productos en otro tenant",
            )
        target_tenant_id = current_user.tenant_id

    results = semantic_search_products(
        db=db,
        tenant_id=target_tenant_id,
        query=query,
        skip=skip,
        limit=limit,
    )

    return [
        ProductSemanticSearchResult(
            product=ProductListResponse.model_validate(product),
            score=score,
        )
        for product, score in results
    ]


# ===== READ (BY ID) =====
@router.get("/{product_id}", response_model=ProductSchema)
def get_product(
        product_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Obtiene un producto por ID.

    **Aislamiento:** Solo puede ver productos de su tenant (excepto superadmin)
    """
    # SuperAdmin puede ver cualquier producto
    if current_user.role.name == "superadmin":
        product = db.query(Product).filter(Product.id == product_id).first()
    else:
        product = crud.get_product_by_id(db, product_id, current_user.tenant_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    return product


# ===== READ (BY SKU) =====
@router.get("/sku/{sku}", response_model=ProductSchema)
def get_product_by_sku(
        sku: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Busca un producto por SKU dentro del tenant.
    Útil para búsquedas rápidas en el POS.
    """
    product = crud.get_product_by_sku(db, sku, current_user.tenant_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con SKU '{sku}' no encontrado"
        )

    return product


# ===== READ (BY BARCODE) =====
@router.get("/barcode/{barcode}", response_model=ProductSchema)
def get_product_by_barcode(
        barcode: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Busca un producto por código de barras.
    Esencial para escaneo en el POS.
    """
    product = crud.get_product_by_barcode(db, barcode, current_user.tenant_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con código de barras '{barcode}' no encontrado"
        )

    return product


# ===== UPDATE =====
@router.put("/{product_id}", response_model=ProductSchema)
def update_product(
        product_id: int,
        product_update: ProductUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_product_write_permission)
):
    """
    Actualiza un producto existente.

    **Permisos requeridos:** inventory, admin, superadmin

    Solo actualiza los campos proporcionados (PATCH behavior).
    """
    # Determinar tenant_id según permisos
    tenant_id = None if current_user.role.name == "superadmin" else current_user.tenant_id

    _validate_unit_conversion(
        purchase_unit=product_update.purchase_unit,
        sale_unit=product_update.sale_unit,
        conversion_factor=product_update.conversion_factor
    )

    return crud.update_product(
        db=db,
        product_id=product_id,
        tenant_id=tenant_id,
        product_update=product_update
    )


# ===== DELETE (SOFT) =====
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
        product_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_product_write_permission)
):
    """
    Elimina un producto (soft delete: marca como inactivo).

    **Permisos requeridos:** inventory, admin, superadmin

    Para eliminación física, contactar al SuperAdmin.
    """
    tenant_id = None if current_user.role.name == "superadmin" else current_user.tenant_id

    crud.delete_product(db=db, product_id=product_id, tenant_id=tenant_id)

    return None


# ===== UTILIDADES =====
@router.get("/utils/low-stock", response_model=List[ProductListResponse])
def get_low_stock_products(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Lista productos con stock por debajo del mínimo.
    Útil para alertas de reposición.

    **Solo muestra productos de su tenant.**
    """
    return crud.get_low_stock_products(db=db, tenant_id=current_user.tenant_id)
