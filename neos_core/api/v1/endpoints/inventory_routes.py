from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from neos_core import schemas, crud
from neos_core.database import models
from neos_core.database.config import get_db
from neos_core.security.security_deps import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.Product, status_code=201)
def create_new_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role.name != "superadmin" and current_user.tenant_id != product.tenant_id:
        raise HTTPException(status_code=403, detail="No puedes crear productos para otro Tenant")
    if current_user.role.name not in ["superadmin", "admin", "inventory"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para crear productos")
    return crud.create_product(db=db, product=product)


@router.get("/", response_model=list[schemas.Product])
def read_products(
        skip: int = 0, limit: int = 100,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    # Si es SuperAdmin, traemos todos los productos de todas las empresas
    if current_user.role.name == "superadmin":
        return db.query(models.Product).offset(skip).limit(limit).all()

    # Si es un usuario normal, filtramos estrictamente por su tenant_id
    return crud.get_products_by_tenant(
        db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit
    )