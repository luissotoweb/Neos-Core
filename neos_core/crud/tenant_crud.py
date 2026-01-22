# neos_core/crud/tenant_crud.py

from sqlalchemy.orm import Session
from neos_core.database import models
from neos_core.schemas import tenant_schema as schemas
from neos_core.onboarding_presets import PRESET_DEFINITIONS

def get_tenant_by_name(db: Session, name: str):
    """Busca un Tenant por su nombre."""
    return db.query(models.Tenant).filter(models.Tenant.name == name).first()

def get_tenant_by_id(db: Session, tenant_id: int):
    """Busca un Tenant por su ID principal."""
    return db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()

def create_tenant(db: Session, tenant: schemas.TenantCreate):
    """Crea un nuevo Tenant en la base de datos."""
    db_tenant = models.Tenant(**tenant.model_dump())
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant


def get_onboarding_preset_by_rubro(db: Session, rubro: str):
    return db.query(models.OnboardingPreset).filter(
        models.OnboardingPreset.rubro == rubro,
        models.OnboardingPreset.is_active.is_(True),
    ).first()


def create_onboarding_preset(db: Session, rubro: str, categories: list[str], active_modules: list[str]):
    preset = models.OnboardingPreset(
        rubro=rubro,
        categories=categories,
        active_modules=active_modules,
        is_active=True,
    )
    db.add(preset)
    db.commit()
    db.refresh(preset)
    return preset


def ensure_onboarding_preset(db: Session, rubro: str):
    preset = get_onboarding_preset_by_rubro(db, rubro=rubro)
    if preset:
        return preset
    preset_definition = PRESET_DEFINITIONS.get(rubro)
    if not preset_definition:
        return None
    return create_onboarding_preset(
        db,
        rubro=rubro,
        categories=preset_definition["categories"],
        active_modules=preset_definition["active_modules"],
    )


def create_tenant_onboarding_config(
    db: Session,
    tenant_id: int,
    rubro: str,
    categories: list[str],
    active_modules: list[str],
    preset_id: int | None,
):
    onboarding = models.TenantOnboardingConfig(
        tenant_id=tenant_id,
        preset_id=preset_id,
        rubro=rubro,
        categories=categories,
        active_modules=active_modules,
    )
    db.add(onboarding)
    db.commit()
    db.refresh(onboarding)
    return onboarding


def get_tenants(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Tenant).offset(skip).limit(limit).all()
