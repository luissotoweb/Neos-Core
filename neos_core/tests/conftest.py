import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from neos_core.database.config import get_db, Base
from neos_core.database import models
from neos_core.security.auth_service import create_access_token
# Importamos passlib para simular el hash, o usa tu función real si prefieres
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    app.dependency_overrides[get_db] = lambda: session
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    return TestClient(app)


@pytest.fixture
def seed_data(db):
    # 1. ROLES
    roles = [
        models.Role(id=1, name="superadmin"),
        models.Role(id=2, name="admin"),
        models.Role(id=3, name="seller")
    ]
    db.add_all(roles)

    # 2. TENANTS
    t1 = models.Tenant(id=1, name="Empresa A", is_active=True)
    t2 = models.Tenant(id=2, name="Empresa B", is_active=True)
    db.add_all([t1, t2])
    db.commit()

    # 3. USUARIOS
    # Super Admin (Para crear tenants y monedas)
    superadmin = models.User(
        id=1, email="super@test.com", hashed_password=pwd_context.hash("pass123"),
        role_id=1, tenant_id=1, is_active=True
    )
    # Admin Tenant 1 (Para crear usuarios y clientes)
    admin_t1 = models.User(
        id=2, email="admin@test.com", hashed_password=pwd_context.hash("pass123"),
        role_id=2, tenant_id=1, is_active=True
    )
    # Vendedor Tenant 1 (Para probar permisos denegados)
    seller_t1 = models.User(
        id=3, email="vendedor@test.com", hashed_password=pwd_context.hash("pass123"),
        role_id=3, tenant_id=1, is_active=True
    )

    db.add_all([superadmin, admin_t1, seller_t1])
    db.commit()
    return {"t1": 1, "super_email": "super@test.com", "admin_email": "admin@test.com"}


@pytest.fixture
def superadmin_headers(seed_data):
    # Generamos token con los datos que espera get_current_user
    token = create_access_token(data={"sub": "super@test.com", "role": "superadmin", "tenant_id": 1})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(seed_data):
    token = create_access_token(data={"sub": "admin@test.com", "role": "admin", "tenant_id": 1})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def seller_headers(seed_data):
    token = create_access_token(data={"sub": "vendedor@test.com", "role": "seller", "tenant_id": 1})
    return {"Authorization": f"Bearer {token}"}