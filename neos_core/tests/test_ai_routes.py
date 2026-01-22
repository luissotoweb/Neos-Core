from types import SimpleNamespace

from fastapi import status

from neos_core.api.v1.endpoints import ai_routes
from neos_core.database import models
from neos_core.security.auth_service import create_access_token


class DummyCatalogAIClient:
    provider = "openai"
    settings = SimpleNamespace(model="gpt-test")

    @classmethod
    def from_env(cls):
        return cls()

    def generate_text(
        self,
        messages,
        temperature=0.2,
        max_tokens=200,
        image_bytes=None,
        image_mime_type=None,
    ):
        return {
            "text": (
                '{"name": "Café", "category": "Bebidas", "tags": ["premium"], '
                '"attributes": {"origen": "Colombia"}}'
            ),
            "raw": {"id": "dummy"},
        }


class DummySQLAIClient:
    provider = "openai"
    settings = SimpleNamespace(model="gpt-test")

    def __init__(self, sql_response):
        self._sql_response = sql_response

    @classmethod
    def from_env(cls):
        return cls("SELECT 1")

    def generate_text(self, messages, temperature=0.1, max_tokens=400):
        return {"text": self._sql_response, "raw": {"id": "dummy"}}


def test_catalog_product_creates_ai_interaction(client, db, admin_headers, monkeypatch):
    monkeypatch.setattr(ai_routes, "AIClient", DummyCatalogAIClient)

    response = client.post(
        "/api/v1/ai/catalog-product",
        data={"metadata": "{\"source\": \"manual\"}"},
        files={"image": ("product.png", b"fake-image", "image/png")},
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["provider"] == "openai"
    assert data["model"] == "gpt-test"
    assert data["catalog"]["name"] == "Café"
    assert data["catalog"]["category"] == "Bebidas"

    interaction = db.query(models.AIInteraction).first()
    assert interaction is not None
    assert interaction.tenant_id == 1
    assert interaction.operation == "catalog_product"
    assert interaction.request_metadata["metadata"]["source"] == "manual"


def test_nlp_to_sql_accepts_tenant_filter(client, db, admin_headers, monkeypatch):
    def _client_factory():
        return DummySQLAIClient("SELECT * FROM sales WHERE tenant_id = 1")

    monkeypatch.setattr(ai_routes, "AIClient", type("Client", (), {"from_env": staticmethod(_client_factory)}))

    response = client.post(
        "/api/v1/ai/nlp-to-sql",
        json={"question": "ventas", "dialect": "postgres"},
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["sql"].startswith("SELECT")
    assert "tenant_id = 1" in data["sql"]

    interaction = db.query(models.AIInteraction).first()
    assert interaction is not None
    assert interaction.operation == "nlp_to_sql"
    assert interaction.response_metadata["has_tenant_filter"] is True


def test_nlp_to_sql_rejects_missing_tenant_filter(client, db, admin_headers, monkeypatch):
    def _client_factory():
        return DummySQLAIClient("SELECT * FROM sales")

    monkeypatch.setattr(ai_routes, "AIClient", type("Client", (), {"from_env": staticmethod(_client_factory)}))

    response = client.post(
        "/api/v1/ai/nlp-to-sql",
        json={"question": "ventas", "dialect": "postgres"},
        headers=admin_headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert db.query(models.AIInteraction).count() == 0


def test_nlp_to_sql_rejects_wrong_tenant_filter(client, db, seed_data, monkeypatch):
    tenant_two_user = models.User(
        email="tenant2@test.com",
        hashed_password="hashed",
        role_id=2,
        tenant_id=2,
        is_active=True,
    )
    db.add(tenant_two_user)
    db.commit()

    token = create_access_token(data={"sub": "tenant2@test.com", "role": "admin", "tenant_id": 2})
    headers = {"Authorization": f"Bearer {token}"}

    def _client_factory():
        return DummySQLAIClient("SELECT * FROM sales WHERE tenant_id = 1")

    monkeypatch.setattr(ai_routes, "AIClient", type("Client", (), {"from_env": staticmethod(_client_factory)}))

    response = client.post(
        "/api/v1/ai/nlp-to-sql",
        json={"question": "ventas", "dialect": "postgres"},
        headers=headers,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
