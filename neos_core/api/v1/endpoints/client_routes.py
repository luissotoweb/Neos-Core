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
def read_clients(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_clients_by_tenant(
        db,
        tenant_id=current_user.tenant_id,
        include_inactive=include_inactive,
    )


@router.delete("/{client_id}", response_model=schemas.Client)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    tenant_filter = None if current_user.role.name == "superadmin" else current_user.tenant_id
    db_client = crud.soft_delete_client(db, client_id=client_id, tenant_id=tenant_filter)
    if not db_client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db_client
