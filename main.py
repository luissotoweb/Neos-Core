# main.py
from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager

# Importaciones de Neos Core
from neos_core.api.v1.api_router import api_router # El nuevo cerebro de rutas
from neos_core.security import auth_router
from neos_core.database.config import Base, engine, get_db
from neos_core.database.seed import seed_roles, seed_tax_data

# --- Configuración de Logging ---
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def initialize_db():
    try:
        Base.metadata.create_all(bind=engine)
        log.info("Tablas verificadas.")
        db = next(get_db())
        try:
            seed_roles(db)
            seed_tax_data(db)
            log.info("Seeding completado.")
        finally:
            db.close()
    except Exception as e:
        log.error(f"Error DB: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_db()
    yield

app = FastAPI(title="Neos Core API", lifespan=lifespan)

# --- REGISTRO DE RUTAS ---

# 1. Autenticación (se mantiene igual)
app.include_router(auth_router.router)

# 2. La API Modular con prefijo de versión
app.include_router(api_router, prefix="/api/v1")