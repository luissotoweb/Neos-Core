from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from typing import List
from contextlib import asynccontextmanager # Se usará para el startup/shutdown (opcional pero recomendado)

# Importaciones de Neos Core
from neos_core.database.config import Base, engine, get_db
from neos_core.database import models  # Importar el módulo models
from neos_core import schemas, crud

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# --- LÓGICA DE INICIALIZACIÓN DE DB ---
def initialize_db():
    """Crea las tablas en la base de datos si no existen."""
    try:
        # Esto usa los modelos importados para crear las tablas
        Base.metadata.create_all(bind=engine)
        log.info("Base de datos inicializada: Tablas 'tenants' y 'users' creadas o ya existentes.")
    except Exception as e:
        log.error(f"Error fatal al inicializar la base de datos: {e}")


# --- FUNCIÓN LIFESPAN (Recomendado por FastAPI, reemplaza on_event) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja los eventos de inicio (startup) y cierre (shutdown)."""
    # Código de STARTUP
    initialize_db()

    yield  # La aplicación está activa aquí

    # Código de SHUTDOWN
    log.info("Cerrando recursos de la aplicación...")


# 1. Instancia de la aplicación (Usando lifespan)
# Nota: Si prefieres la sintaxis antigua, mantén la línea: app = FastAPI(title="Neos Core API") y el bloque @app.on_event("startup")
app = FastAPI(title="Neos Core API", lifespan=lifespan)

# Si usas la sintaxis antigua, ELIMINA el 'lifespan' de arriba y usa este bloque:
# @app.on_event("startup")
# def startup_event():
#     initialize_db()


# --- ENDPOINTS (RUTAS) ---

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    """Endpoint de prueba de conectividad y sesión DB."""
    return {"message": "¡Neos Core - DB Conectado y Listo! (V-0.0.1"}


# ----------------------------------------------------
# CRUD: TENANT
# ----------------------------------------------------

@app.post("/tenants/", response_model=schemas.Tenant, status_code=201)
def create_new_tenant(
        tenant: schemas.TenantCreate,
        db: Session = Depends(get_db)
):
    """Crea un nuevo cliente (Tenant) en el sistema."""
    db_tenant = crud.get_tenant_by_name(db, name=tenant.name)
    if db_tenant:
        raise HTTPException(
            status_code=400,
            detail="El nombre de Tenant ya está registrado."
        )

    return crud.create_tenant(db=db, tenant=tenant)

@app.get("/tenants/", response_model=List[schemas.Tenant])
def read_tenants(db: Session = Depends(get_db)):
    """Lista todos los clientes (Tenants) registrados."""
    tenants = db.query(models.Tenant).all()
    return tenants

@app.get("/tenants/{tenant_id}", response_model=schemas.Tenant)
def read_tenant_by_id(
    tenant_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene la información de un Tenant específico por su ID."""
    db_tenant = crud.get_tenant_by_id(db, tenant_id=tenant_id)
    if db_tenant is None:
        raise HTTPException(
            status_code=404,
            detail="Tenant no encontrado."
        )
    return db_tenant

# ----------------------------------------------------
# CRUD: USER
# ----------------------------------------------------

@app.post("/users/", response_model=schemas.User, status_code=201)
def create_new_user(
        user: schemas.UserCreate,
        db: Session = Depends(get_db)
):
    """
    Crea un nuevo usuario en el sistema, requiere un tenant_id válido.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="El correo electrónico ya está registrado."
        )

    db_tenant = db.query(models.Tenant).filter(models.Tenant.id == user.tenant_id).first()
    if not db_tenant:
        raise HTTPException(
            status_code=404,
            detail=f"Tenant con ID {user.tenant_id} no encontrado. No se puede crear el usuario."
        )

    return crud.create_user(db=db, user=user)