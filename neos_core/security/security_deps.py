# neos_core/security/security_deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from neos_core.database.config import get_db
from neos_core.database import models
from neos_core.security.auth_config import SECRET_KEY, ALGORITHM
from neos_core import schemas, crud

# Configuramos dónde debe buscar FastAPI el token (en la ruta /token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    """
    Dependencia para validar el token JWT y retornar el objeto usuario.
    Si el token es inválido o el usuario no existe, lanza una excepción 401.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token de acceso",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. Decodificar el Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        tenant_id: int = payload.get("tenant_id")

        if email is None or tenant_id is None:
            raise credentials_exception

        token_data = schemas.TokenData(email=email)

    except JWTError:
        raise credentials_exception

    # 2. Buscar al usuario en la base de datos
    user = crud.get_user_by_email(db, email=token_data.email)

    if user is None:
        raise credentials_exception

    # 3. Retornar el usuario (esto permite que el endpoint sepa quién llama)
    return user