# main.py
"""
Punto de entrada principal de Neos Core API
FastAPI application con configuración de CORS y lifespan
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

# Importaciones de Neos Core
from neos_core.api.v1.api_router import api_router
from neos_core.security.auth_router import router as auth_router
from neos_core.database.config import engine

# --- Configuración de Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager para FastAPI
    Se ejecuta al iniciar y cerrar la aplicación
    """
    # Startup
    log.info("🚀 Iniciando Neos Core API...")

    # Verificar conexión a base de datos
    try:
        with engine.connect() as conn:
            log.info("✓ Conexión a base de datos exitosa")
    except Exception as e:
        log.error(f"❌ Error al conectar con la base de datos: {e}")
        log.error("   Ejecuta: python init_database.py")
        raise

    log.info("✓ Neos Core API iniciada correctamente")

    yield  # Aplicación corriendo

    # Shutdown
    log.info("🔴 Cerrando Neos Core API...")


# --- Crear aplicación FastAPI ---
app = FastAPI(
    title="Neos Core API",
    description="Sistema de gestión multi-tenant con módulo de ventas",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- Configuración de CORS ---
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REGISTRO DE RUTAS ---

# 1. Autenticación
app.include_router(auth_router)

# 2. API v1 Modular
app.include_router(api_router, prefix="/api/v1")


# --- Health Check ---
@app.get("/health", tags=["Health"])
async def health_check():
    """Verificación de estado del servidor"""
    return {
        "status": "healthy",
        "service": "Neos Core API",
        "version": "1.0.0"
    }


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz"""
    return {
        "message": "Bienvenido a Neos Core API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )