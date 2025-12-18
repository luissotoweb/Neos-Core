# neos_core/security/auth_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from neos_core.database.config import get_db
from neos_core import crud, schemas
from neos_core.security import auth_service

router = APIRouter(tags=["Autenticación"])


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    """
    Endpoint estándar OAuth2 para obtener un token de acceso (Login).
    Recibe: username (email) y password.
    Devuelve: JWT access_token.
    """
    # 1. Buscar al usuario por email
    # Nota: OAuth2 usa el campo 'username', nosotros lo mapeamos a nuestro 'email'
    user = crud.get_user_by_email(db, email=form_data.username)

    # 2. Verificar credenciales
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas (Email o contraseña inválidos)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Verificar si el usuario está activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo."
        )

    # 4. Generar el Token JWT
    # Guardamos el email (sub) y el tenant_id en el token
    access_token = auth_service.create_access_token(
        data={"sub": user.email, "tenant_id": user.tenant_id}
    )

    return {"access_token": access_token, "token_type": "bearer"}