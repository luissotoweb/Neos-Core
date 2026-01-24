# neos_core/crud/config_crud.py
"""
CRUD operations para configuración: Monedas y Puntos de Venta
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status

# Importar desde archivos separados (NO desde tax_models.py)
from neos_core.database.models import Currency, PointOfSale, TaxRate
from neos_core.schemas.config_schema import (
    CurrencyCreate,
    PointOfSaleCreate,
    PointOfSaleUpdate,
    TaxRateCreate,
    TaxRateUpdate
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


# ============ CRUD TASAS DE IMPUESTO ============

def get_tax_rates_by_tenant(
        db: Session,
        tenant_id: int,
        is_active: Optional[bool] = None
) -> List[TaxRate]:
    """Lista tasas de impuesto por tenant"""
    query = db.query(TaxRate).filter(TaxRate.tenant_id == tenant_id)

    if is_active is not None:
        query = query.filter(TaxRate.is_active == is_active)

    return query.all()


def get_tax_rate_by_id(db: Session, tax_rate_id: int, tenant_id: int) -> Optional[TaxRate]:
    """Obtiene una tasa de impuesto por ID con aislamiento de tenant"""
    return db.query(TaxRate).filter(
        TaxRate.id == tax_rate_id,
        TaxRate.tenant_id == tenant_id
    ).first()


def get_tax_rate_by_name(db: Session, name: str, tenant_id: int) -> Optional[TaxRate]:
    """Busca una tasa de impuesto por nombre dentro del tenant"""
    return db.query(TaxRate).filter(
        TaxRate.name == name,
        TaxRate.tenant_id == tenant_id
    ).first()


def create_tax_rate(db: Session, tax_rate: TaxRateCreate) -> TaxRate:
    """Crea una tasa de impuesto para el tenant"""
    existing = get_tax_rate_by_name(db, tax_rate.name, tax_rate.tenant_id)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una tasa de impuesto con el nombre '{tax_rate.name}' en tu empresa"
        )

    db_tax_rate = TaxRate(**tax_rate.model_dump())
    db.add(db_tax_rate)
    db.commit()
    db.refresh(db_tax_rate)
    return db_tax_rate


def update_tax_rate(
        db: Session,
        tax_rate_id: int,
        tenant_id: int,
        tax_rate_update: TaxRateUpdate
) -> TaxRate:
    """Actualiza una tasa de impuesto existente"""
    db_tax_rate = get_tax_rate_by_id(db, tax_rate_id, tenant_id)

    if not db_tax_rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tasa de impuesto no encontrada"
        )

    update_data = tax_rate_update.model_dump(exclude_unset=True)

    if "name" in update_data:
        existing = get_tax_rate_by_name(db, update_data["name"], tenant_id)
        if existing and existing.id != db_tax_rate.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una tasa de impuesto con el nombre '{update_data['name']}' en tu empresa"
            )

    for field, value in update_data.items():
        setattr(db_tax_rate, field, value)

    db.commit()
    db.refresh(db_tax_rate)
    return db_tax_rate


def delete_tax_rate(db: Session, tax_rate_id: int, tenant_id: int) -> bool:
    """Elimina (soft delete) una tasa de impuesto"""
    db_tax_rate = get_tax_rate_by_id(db, tax_rate_id, tenant_id)

    if not db_tax_rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tasa de impuesto no encontrada"
        )

    db_tax_rate.is_active = False
    db.commit()

    return True
