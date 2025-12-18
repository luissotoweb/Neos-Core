# neos_core/security/auth_service.py

from datetime import datetime, timedelta, timezone
from jose import jwt
from neos_core.security.auth_config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict):
    """
    Genera un JWT firmado con los datos del usuario (claims).
    """
    to_encode = data.copy()

    # Definir cuándo expira el token
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Agregar la expiración al payload (claim 'exp')
    to_encode.update({"exp": expire})

    # Codificar y firmar el token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt