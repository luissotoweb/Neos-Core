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
    ensure_tenant_categories(db, tenant_id=tenant_id, categories=categories)
    ensure_tenant_active_modules(db, tenant_id=tenant_id, active_modules=active_modules)
    return onboarding


def get_tenants(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Tenant).offset(skip).limit(limit).all()


def get_category_by_name(db: Session, tenant_id: int, name: str):
    return db.query(models.TenantCategory).filter(
        models.TenantCategory.tenant_id == tenant_id,
        models.TenantCategory.name == name,
    ).first()


def create_category(db: Session, tenant_id: int, name: str):
    existing = get_category_by_name(db, tenant_id=tenant_id, name=name)
    if existing:
        return existing
    category = models.TenantCategory(
        tenant_id=tenant_id,
        name=name,
        is_active=True,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def ensure_tenant_categories(db: Session, tenant_id: int, categories: list[str]):
    cleaned_categories = [category.strip() for category in categories if category and category.strip()]
    if not cleaned_categories:
        return []

    existing_categories = db.query(models.TenantCategory).filter(
        models.TenantCategory.tenant_id == tenant_id,
        models.TenantCategory.name.in_(cleaned_categories),
    ).all()
    existing_names = {category.name for category in existing_categories}

    new_categories = [
        models.TenantCategory(tenant_id=tenant_id, name=category, is_active=True)
        for category in cleaned_categories
        if category not in existing_names
    ]
    if new_categories:
        db.add_all(new_categories)
        db.commit()
        for category in new_categories:
            db.refresh(category)
    return existing_categories + new_categories


def get_active_module_by_key(db: Session, tenant_id: int, module_key: str):
    return db.query(models.TenantActiveModule).filter(
        models.TenantActiveModule.tenant_id == tenant_id,
        models.TenantActiveModule.module_key == module_key,
    ).first()


def create_active_module(db: Session, tenant_id: int, module_key: str):
    existing = get_active_module_by_key(db, tenant_id=tenant_id, module_key=module_key)
    if existing:
        return existing
    module = models.TenantActiveModule(
        tenant_id=tenant_id,
        module_key=module_key,
        is_active=True,
    )
    db.add(module)
    db.commit()
    db.refresh(module)
    return module


def ensure_tenant_active_modules(db: Session, tenant_id: int, active_modules: list[str]):
    cleaned_modules = [module.strip().lower() for module in active_modules if module and module.strip()]
    if not cleaned_modules:
        return []

    existing_modules = db.query(models.TenantActiveModule).filter(
        models.TenantActiveModule.tenant_id == tenant_id,
        models.TenantActiveModule.module_key.in_(cleaned_modules),
    ).all()
    existing_keys = {module.module_key for module in existing_modules}

    new_modules = [
        models.TenantActiveModule(tenant_id=tenant_id, module_key=module_key, is_active=True)
        for module_key in cleaned_modules
        if module_key not in existing_keys
    ]
    if new_modules:
        db.add_all(new_modules)
        db.commit()
        for module in new_modules:
            db.refresh(module)
    return existing_modules + new_modules
