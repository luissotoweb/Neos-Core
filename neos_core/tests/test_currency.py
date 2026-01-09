import pytest

def test_create_currency(client, superadmin_headers):
    payload = {"name": "Dolar", "code": "USD", "symbol": "$"}
    response = client.post("/api/v1/config/currencies", json=payload, headers=superadmin_headers)
    assert response.status_code in [200, 201]
    assert response.json()["code"] == "USD"

def test_create_currency_forbidden_for_seller(client, seller_headers):
    # Un vendedor no puede crear monedas
    payload = {"name": "Yen", "code": "JPY", "symbol": "¥"}
    response = client.post("/api/v1/config/currencies", json=payload, headers=seller_headers)
    assert response.status_code == 403

def test_get_currencies_public(client, seller_headers):
    # Pero sí puede verlas
    response = client.get("/api/v1/config/currencies", headers=seller_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)