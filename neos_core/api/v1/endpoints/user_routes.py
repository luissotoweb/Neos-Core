from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from neos_core import schemas, crud
from neos_core.database import models
from neos_core.database.config import get_db
from neos_core.security.security_deps import get_current_user

router = APIRouter()


@router.post("/", response_model=schemas.User, status_code=201)
def create_new_user(
        user: schemas.UserCreate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    if current_user.role.name != "superadmin" and current_user.tenant_id != user.tenant_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear usuarios en otros Tenants.")
    if current_user.role.name not in ["superadmin", "admin"]:
        raise HTTPException(status_code=403, detail="Tu rol no tiene permisos para crear usuarios.")

    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")
    return crud.create_user(db=db, user=user)


@router.get("/", response_model=list[schemas.User])
def read_users(
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    return crud.get_visible_users(db, current_user=current_user, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=schemas.User)
def read_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    # Verificación de permisos básica: Superadmin ve todo, otros ven su propio tenant
    db_user = crud.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if current_user.role.name != "superadmin" and current_user.tenant_id != db_user.tenant_id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este usuario")

    return db_user


@router.put("/{user_id}", response_model=schemas.User)
@router.patch("/{user_id}", response_model=schemas.User)
def update_user(
        user_id: int,
        user_update: schemas.UserUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    if current_user.role.name not in ["superadmin", "admin"]:
        raise HTTPException(status_code=403, detail="Tu rol no tiene permisos para actualizar usuarios.")

    db_user = crud.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if current_user.role.name != "superadmin" and current_user.tenant_id != db_user.tenant_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar usuarios de otros Tenants.")

    update_data = user_update.model_dump(exclude_unset=True)
    if current_user.role.name != "superadmin":
        if "tenant_id" in update_data and update_data["tenant_id"] != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para cambiar el Tenant del usuario.")

    if "email" in update_data and update_data["email"] != db_user.email:
        existing = crud.get_user_by_email(db, email=update_data["email"])
        if existing:
            raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")

    return crud.update_user(db=db, user_id=user_id, user_update=user_update)
