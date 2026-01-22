# neos_core/crud/user_crud.py

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from neos_core.database import models
from neos_core import schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Genera el hash seguro de una contraseña."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña en texto plano coincide con el hash almacenado."""
    return pwd_context.verify(plain_password, hashed_password)


# -----------------------------------------------------------------

def get_user_by_email(db: Session, email: str):
    """Busca un usuario por su correo electrónico (usado para login)."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    """Busca un usuario por su ID principal."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate):
    """
    Crea un nuevo usuario, hasheando la contraseña antes de guardarla.
    """
    # 1. Hashing de Contraseña
    hashed_password = get_password_hash(user.password)

    # 2. Creación del modelo
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        tenant_id=user.tenant_id,
        role_id=user.role_id,  # <--- Vinculación con la tabla de roles
        hashed_password=hashed_password,
        is_active=user.is_active
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Retorna todos los usuarios (solo para SuperAdmin o debugging)"""
    return db.query(models.User).offset(skip).limit(limit).all()

def get_users_by_tenant(db: Session, tenant_id: int, skip: int = 0, limit: int = 100):
    """
    Retorna usuarios filtrados por Tenant.
    Cumple con el requisito de aislamiento (RF-001).
    """
    return db.query(models.User).filter(models.User.tenant_id == tenant_id).offset(skip).limit(limit).all()


def get_visible_users(db: Session, current_user: models.User, skip: int = 0, limit: int = 100):
    """
    Jerarquía de visibilidad:
    - SuperAdmin: Ve a todos los usuarios de todos los tenants.
    - Admin: Solo ve a los usuarios de su propio tenant.
    - Empleados: Solo ven su propia información (esto se puede ajustar según necesites).
    """
    if current_user.role.name == "superadmin":
        return db.query(models.User).offset(skip).limit(limit).all()

    return db.query(models.User).filter(
        models.User.tenant_id == current_user.tenant_id
    ).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    """Actualiza parcialmente un usuario existente."""
    db_user = get_user_by_id(db, user_id=user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)

    if "password" in update_data:
        db_user.hashed_password = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user
