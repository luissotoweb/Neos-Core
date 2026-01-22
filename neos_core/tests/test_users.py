import pytest
from neos_core.database import models


def test_user_creation_and_visibility(client, superadmin_headers):
    # Test crear usuario
    new_user = {
        "email": "user@test.com", "password": "password",
        "full_name": "Test User", "role_id": 3, "tenant_id": 1
    }
    res = client.post("/api/v1/users/", json=new_user, headers=superadmin_headers)
    assert res.status_code == 201

    # Probamos el GET / que devuelve la lista
    res = client.get("/api/v1/users/", headers=superadmin_headers)
    assert res.status_code == 200
    assert any(u["email"] == "user@test.com" for u in res.json())


def test_seed_execution(db):
    # Esto valida que el seed corra sin errores
    from neos_core.database.seed import seed_roles, seed_tax_data
    seed_roles(db)
    seed_tax_data(db)
    assert True


def test_auth_errors(client):
    # Probamos credenciales incorrectas
    res = client.post("/token", data={"username": "admin@test.com", "password": "wrongpassword"})
    assert res.status_code == 401
    assert "Credenciales incorrectas" in res.json()["detail"]


def test_user_creation_permissions(client, seller_headers):
    # CORREGIDO: Usamos 'seller_headers' que ya existe en conftest.py
    # Un vendedor (rol 3) NO debería poder crear usuarios
    payload = {
        "email": "new_admin_hack@test.com",
        "password": "password123",
        "full_name": "Hacker",
        "tenant_id": 1,
        "role_id": 2
    }
    res = client.post("/api/v1/users/", json=payload, headers=seller_headers)
    assert res.status_code == 403  # Forbidden


def test_create_duplicate_user(client, admin_headers):
    # CORREGIDO: Creamos el usuario DENTRO del test para asegurar que existe y provocar el error
    payload = {
        "email": "duplicate_check@test.com",
        "password": "password123",
        "full_name": "Duplicate Tester",
        "tenant_id": 1,
        "role_id": 2
    }

    # 1. Primera vez: Creación exitosa (201)
    res1 = client.post("/api/v1/users/", json=payload, headers=admin_headers)
    assert res1.status_code == 201

    # 2. Segunda vez: Fallo por duplicado (400)
    res2 = client.post("/api/v1/users/", json=payload, headers=admin_headers)
    assert res2.status_code == 400
    # Validamos que el mensaje mencione que ya está registrado
    assert "registrado" in res2.json()["detail"]

def test_login_non_existent_user(client):
    # Usuario que no existe en la DB
    res = client.post("/token", data={"username": "ghost@test.com", "password": "password"})
    assert res.status_code == 401
    assert "Credenciales incorrectas" in res.json()["detail"]


def test_update_user_role_email_status(client, superadmin_headers):
    payload = {
        "email": "update_me@test.com",
        "password": "password123",
        "full_name": "Update Me",
        "tenant_id": 1,
        "role_id": 2
    }
    res = client.post("/api/v1/users/", json=payload, headers=superadmin_headers)
    assert res.status_code == 201
    user_id = res.json()["id"]

    update_payload = {
        "email": "updated_user@test.com",
        "role_id": 3,
        "is_active": False
    }
    res = client.patch(f"/api/v1/users/{user_id}", json=update_payload, headers=superadmin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "updated_user@test.com"
    assert data["role_id"] == 3
    assert data["is_active"] is False



def test_get_user_by_id_coverage(client, db, superadmin_headers):
    db.commit()

    user_in_db = db.query(models.User).filter(models.User.email == "super@test.com").first()

    if not user_in_db:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        user_in_db = models.User(
            email="super@test.com",
            hashed_password=pwd_context.hash("pass123"),
            role_id=1,
            tenant_id=1,
            is_active=True
        )
        db.add(user_in_db)
        db.commit()
        db.refresh(user_in_db)

    target_id = user_in_db.id

    res = client.get(f"/api/v1/users/{target_id}", headers=superadmin_headers)

    assert res.status_code == 200
    assert res.json()["id"] == target_id


def test_login_wrong_user(client):
    # Cubre la línea de 'usuario no encontrado' en auth_router
    res = client.post("/token", data={"username": "noexiste@test.com", "password": "123"})
    assert res.status_code == 401
