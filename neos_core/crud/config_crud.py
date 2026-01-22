# neos_core/crud/config_crud.py
"""
CRUD operations para configuración: Monedas y Puntos de Venta
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status

# Importar desde archivos separados (NO desde tax_models.py)
from neos_core.database.models import Currency, PointOfSale
from neos_core.schemas.config_schema import (
    CurrencyCreate,
    CurrencyUpdate,
    PointOfSaleCreate,
    PointOfSaleUpdate
)


# ============ CRUD MONEDAS ============

def get_currencies(db: Session, is_active: Optional[bool] = None) -> List[Currency]:
    """
    Lista todas las monedas del sistema
    Opcionalmente filtra por estado activo/inactivo
    """
    query = db.query(Currency)

    if is_active is not None:
        query = query.filter(Currency.is_active == is_active)

    return query.all()


def get_currency_by_id(db: Session, currency_id: int) -> Optional[Currency]:
    """Obtiene una moneda por ID"""
    return db.query(Currency).filter(Currency.id == currency_id).first()


def get_currency_by_code(db: Session, code: str) -> Optional[Currency]:
    """Busca una moneda por código (USD, ARS, etc.)"""
    return db.query(Currency).filter(Currency.code == code).first()


def create_currency(db: Session, currency: CurrencyCreate) -> Currency:
    """
    Crea una nueva moneda (solo SuperAdmin)
    Verifica que no exista duplicado por código
    """
    existing = get_currency_by_code(db, currency.code)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una moneda con el código '{currency.code}'"
        )

    db_currency = Currency(**currency.model_dump())
    db.add(db_currency)
    db.commit()
    db.refresh(db_currency)
    return db_currency


def update_currency(db: Session, currency_id: int, currency_update: CurrencyUpdate) -> Currency:
    """Actualiza una moneda existente"""
    db_currency = get_currency_by_id(db, currency_id)
    if not db_currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Moneda no encontrada"
        )

    update_data = currency_update.model_dump(exclude_unset=True)

    if "code" in update_data and update_data["code"] != db_currency.code:
        existing = get_currency_by_code(db, update_data["code"])
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una moneda con el código '{update_data['code']}'"
            )

    for field, value in update_data.items():
        setattr(db_currency, field, value)

    db.commit()
    db.refresh(db_currency)
    return db_currency


# ============ CRUD PUNTOS DE VENTA ============

def get_pos_by_tenant(
        db: Session,
        tenant_id: int,
        is_active: Optional[bool] = None
) -> List[PointOfSale]:
    """
    Lista puntos de venta de un tenant
    Opcionalmente filtra por estado activo/inactivo
    """
    query = db.query(PointOfSale).filter(PointOfSale.tenant_id == tenant_id)

    if is_active is not None:
        query = query.filter(PointOfSale.is_active == is_active)

    return query.all()


def get_pos_by_id(db: Session, pos_id: int, tenant_id: int) -> Optional[PointOfSale]:
    """
    Obtiene un punto de venta por ID con aislamiento de tenant
    """
    return db.query(PointOfSale).filter(
        PointOfSale.id == pos_id,
        PointOfSale.tenant_id == tenant_id
    ).first()

def get_pos_by_id_global(db: Session, pos_id: int) -> Optional[PointOfSale]:
    """Obtiene un punto de venta por ID sin restricción de tenant"""
    return db.query(PointOfSale).filter(PointOfSale.id == pos_id).first()


def get_pos_by_code(db: Session, code: str, tenant_id: int) -> Optional[PointOfSale]:
    """Busca un punto de venta por código dentro del tenant"""
    return db.query(PointOfSale).filter(
        PointOfSale.code == code,
        PointOfSale.tenant_id == tenant_id
    ).first()


def create_pos(db: Session, pos: PointOfSaleCreate) -> PointOfSale:
    """
    Crea un nuevo punto de venta
    Verifica que no exista duplicado por código en el tenant
    """
    existing = get_pos_by_code(db, pos.code, pos.tenant_id)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un punto de venta con el código '{pos.code}' en tu empresa"
        )

    db_pos = PointOfSale(**pos.model_dump())
    db.add(db_pos)
    db.commit()
    db.refresh(db_pos)
    return db_pos


def update_pos(
        db: Session,
        pos_id: int,
        tenant_id: int,
        pos_update: PointOfSaleUpdate
) -> PointOfSale:
    """Actualiza un punto de venta existente"""
    db_pos = get_pos_by_id(db, pos_id, tenant_id)

    if not db_pos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Punto de venta no encontrado"
        )

    # Actualizar solo los campos que vinieron en el request
    update_data = pos_update.model_dump(exclude_unset=True)

    if "code" in update_data and update_data["code"] != db_pos.code:
        existing = get_pos_by_code(db, update_data["code"], tenant_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un punto de venta con el código '{update_data['code']}' en tu empresa"
            )

    for field, value in update_data.items():
        setattr(db_pos, field, value)

    db.commit()
    db.refresh(db_pos)
    return db_pos


def delete_pos(db: Session, pos_id: int, tenant_id: int) -> bool:
    """Elimina (soft delete) un punto de venta"""
    db_pos = get_pos_by_id(db, pos_id, tenant_id)

    if not db_pos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Punto de venta no encontrado"
        )

    # Soft delete
    db_pos.is_active = False
    db.commit()

    return True
