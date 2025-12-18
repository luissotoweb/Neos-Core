# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from typing import List
from contextlib import asynccontextmanager

# Importaciones de Neos Core
from neos_core.security import auth_router
from neos_core.security.security_deps import get_current_user
from neos_core.database.config import Base, engine, get_db
from neos_core.database import models
from neos_core import schemas, crud
from neos_core.database.seed import seed_roles  # <--- Importamos el seeder

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# --- LÓGICA DE INICIALIZACIÓN DE DB ---
def initialize_db():
    """Crea las tablas y puebla los roles iniciales."""
    try:
        # Crea las tablas (incluyendo la nueva tabla 'roles')
        Base.metadata.create_all(bind=engine)
        log.info("Tablas de la base de datos verificadas/creadas.")

        # Ejecutamos el seeding de roles
        db = next(get_db())
        try:
            seed_roles(db)
            log.info("Seeding de roles completado exitosamente.")
        finally:
            db.close()

    except Exception as e:
        log.error(f"Error fatal al inicializar la base de datos: {e}")


# --- FUNCIÓN LIFESPAN ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja los eventos de inicio (startup) y cierre."""
    initialize_db()  #
    yield
    log.info("Cerrando recursos de la aplicación...")


app = FastAPI(title="Neos Core API", lifespan=lifespan)


# --- ENDPOINTS PROTEGIDOS POR ROLES ---

@app.post("/tenants/", response_model=schemas.Tenant, status_code=201)
def create_new_tenant(
        tenant: schemas.TenantCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)  #
):
    """Solo el SuperAdmin puede crear nuevos Tenants."""
    # Verificamos el rol del usuario actual
    if current_user.role.name != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operación permitida solo para SuperAdmin."
        )

    db_tenant = crud.get_tenant_by_name(db, name=tenant.name)
    if db_tenant:
        raise HTTPException(status_code=400, detail="El nombre de Tenant ya está registrado.")

    return crud.create_tenant(db=db, tenant=tenant)


@app.post("/users/", response_model=schemas.User, status_code=201)
def create_new_user(
        user: schemas.UserCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)  #
):
    """
    Un admin solo puede crear usuarios para su propio tenant.
    Un superadmin puede crear usuarios en cualquier tenant.
    """
    # 1. Validación de jerarquía: Si no es superadmin, solo puede crear en su propio tenant
    if current_user.role.name != "superadmin" and current_user.tenant_id != user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para crear usuarios en otros Tenants."
        )

    # 2. Validación de rol: Solo 'admin' o 'superadmin' pueden crear usuarios
    if current_user.role.name not in ["superadmin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu rol no tiene permisos para crear usuarios."
        )

    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")

    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    # Ahora el SuperAdmin podrá ver la lista global
    return crud.get_visible_users(db, current_user=current_user, skip=skip, limit=limit)


app.include_router(auth_router.router)