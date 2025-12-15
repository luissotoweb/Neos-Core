# neos_core/crud/user_crud.py

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from neos_core.database import models
from neos_core import schemas

# --- CONFIGURACIÓN DE SEGURIDAD (Se queda con el User CRUD) ---
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
        hashed_password=hashed_password,
        is_active=user.is_active,
        is_superuser=user.is_superuser
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user