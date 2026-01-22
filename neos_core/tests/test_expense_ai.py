from types import SimpleNamespace

from neos_core.database import models
from neos_core.api.v1.endpoints import ai_routes


class DummyAIClient:
    provider = "openai"
    settings = SimpleNamespace(model="gpt-test")

    @classmethod
    def from_env(cls):
        return cls()

    def generate_text(self, messages, temperature=0.2, max_tokens=200, image_bytes=None, image_mime_type=None):
        return {"text": '{"account_code": "6001"}', "raw": {"id": "dummy"}}


def test_expense_suggest_creates_expense_and_ai_interaction(client, db, admin_headers, monkeypatch):
    monkeypatch.setattr(ai_routes, "AIClient", DummyAIClient)

    payload = {"description": "Compra de papelería", "amount": 125.50}
    response = client.post("/api/v1/ai/expense-suggest", json=payload, headers=admin_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["suggested_account"] == "6001"
    assert data["provider"] == "openai"
    assert data["model"] == "gpt-test"
    assert data["expense"]["description"] == payload["description"]
    assert float(data["expense"]["amount"]) == payload["amount"]

    expense = db.query(models.Expense).first()
    assert expense is not None
    assert expense.suggested_account == "6001"

    interaction = db.query(models.AIInteraction).first()
    assert interaction is not None
    assert interaction.operation == "expense_suggest_account"
    assert interaction.request_metadata["description"] == payload["description"]
