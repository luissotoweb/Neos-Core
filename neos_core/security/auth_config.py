# neos_core/security/auth_config.py

# --- CONFIGURACIÓN DE SEGURIDAD ---
import os

from dotenv import load_dotenv

# IMPORTANTE: En producción, esto debe ser un secreto real generado aleatoriamente.
# Puedes generar uno ejecutando en terminal: openssl rand -hex 32
DEFAULT_INSECURE_SECRET = "neos-inventory-super-secret-key-change-me-in-prod"

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY no está configurada. Define la variable de entorno SECRET_KEY."
    )
if SECRET_KEY == DEFAULT_INSECURE_SECRET:
    raise RuntimeError(
        "SECRET_KEY usa el valor inseguro por defecto. "
        "Define un valor seguro generado aleatoriamente."
    )

# Algoritmo de firma (HS256 es estándar y seguro para esto)
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Tiempo de vida del token (30 minutos es estándar para bancos/ERP)
_expire_minutes = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(_expire_minutes)
except ValueError as exc:
    raise RuntimeError(
        "ACCESS_TOKEN_EXPIRE_MINUTES debe ser un entero en minutos."
    ) from exc
