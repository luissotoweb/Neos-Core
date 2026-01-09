import pytest
from neos_core.crud import user_crud, tenant_crud
from neos_core.database import models
from neos_core.security.auth_service import create_access_token


def test_invalid_token_format(client):
    res = client.get("/api/v1/users/", headers={"Authorization": "Bearer token_falso"})
    assert res.status_code in [401, 403]


def test_inactive_user_logic(client, db):
    email_test = "inactive@test.com"
    # Borramos si existe para evitar conflictos de unicidad
    db.query(models.User).filter(models.User.email == email_test).delete()

    user = models.User(email=email_test, hashed_password="fake", is_active=False, role_id=1, tenant_id=1)
    db.add(user)
    db.commit()

    token = create_access_token(data={"sub": email_test, "role": "admin", "tenant_id": 1})
    res = client.get("/api/v1/users/", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code >= 400


def test_direct_crud_operations(db):
    # Aseguramos existencia del tenant con ID 1
    t = db.query(models.Tenant).filter(models.Tenant.id == 1).first()
    if not t:
        t = models.Tenant(id=1, name="Empresa Test CRUD", tax_id="123-CRUD")
        db.add(t)
        db.commit()

    db.refresh(t)  # Crucial: Refresca el objeto para que sus atributos sean accesibles

    # Ejecutamos CRUD con datos garantizados
    users = user_crud.get_users(db)
    tenant_by_id = tenant_crud.get_tenant_by_id(db, tenant_id=t.id)
    tenant_by_name = tenant_crud.get_tenant_by_name(db, name=t.name)

    assert tenant_by_id is not None
    assert tenant_by_name is not None
    assert tenant_by_name.name == "Empresa Test CRUD"


def test_database_config_coverage():
    from neos_core.database.config import engine
    with engine.connect() as conn:
        assert conn is not None