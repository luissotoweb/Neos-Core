# neos_core/security/auth_config.py

# --- CONFIGURACIÓN DE SEGURIDAD ---

# IMPORTANTE: En producción, esto debe ser un secreto real generado aleatoriamente.
# Puedes generar uno ejecutando en terminal: openssl rand -hex 32
SECRET_KEY = "neos-inventory-super-secret-key-change-me-in-prod"

# Algoritmo de firma (HS256 es estándar y seguro para esto)
ALGORITHM = "HS256"

# Tiempo de vida del token (30 minutos es estándar para bancos/ERP)
ACCESS_TOKEN_EXPIRE_MINUTES = 30