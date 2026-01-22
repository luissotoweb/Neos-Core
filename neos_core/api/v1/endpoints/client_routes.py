from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from neos_core.database.config import get_db
from neos_core.security.security_deps import get_current_user
from neos_core.database import models
from neos_core.schemas import client_schema as schemas
from neos_core.crud import client_crud as crud

router = APIRouter()


@router.post("/", response_model=schemas.Client)
def create_new_client(client: schemas.ClientCreate, db: Session = Depends(get_db),
                      current_user: models.User = Depends(get_current_user)):
    # Protección de Tenant
    if current_user.role.name != "superadmin" and client.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="No puedes crear clientes para otra empresa")

    # Verificar si ya existe por CUIT/DNI en este tenant
    existing = crud.get_client_by_tax_id(db, tax_id=client.tax_id, tenant_id=client.tenant_id)
    if existing:
        raise HTTPException(status_code=400, detail="Este cliente (Tax ID) ya está registrado en tu empresa")

    return crud.create_client(db=db, client=client)


@router.get("/", response_model=List[schemas.Client])
def read_clients(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_clients_by_tenant(db, tenant_id=current_user.tenant_id)


@router.put("/{client_id}", response_model=schemas.Client)
@router.patch("/{client_id}", response_model=schemas.Client)
def update_client(
        client_id: int,
        client_update: schemas.ClientUpdate,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    if current_user.role.name == "superadmin":
        db_client = crud.get_client_by_id_global(db, client_id=client_id)
    else:
        db_client = crud.get_client_by_id(db, client_id=client_id, tenant_id=current_user.tenant_id)

    if not db_client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    if current_user.role.name != "superadmin" and db_client.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="No puedes actualizar clientes de otra empresa")

    update_data = client_update.model_dump(exclude_unset=True)
    if "tax_id" in update_data and update_data["tax_id"] != db_client.tax_id:
        existing = crud.get_client_by_tax_id(db, tax_id=update_data["tax_id"], tenant_id=db_client.tenant_id)
        if existing and existing.id != db_client.id:
            raise HTTPException(status_code=400, detail="Este cliente (Tax ID) ya está registrado en tu empresa")

    return crud.update_client(db, client_id=db_client.id, tenant_id=db_client.tenant_id, client_update=client_update)
