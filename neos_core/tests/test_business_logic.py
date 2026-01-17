import pytest


# --- TESTS DE INVENTARIO ---
def test_inventory_full_coverage(client, admin_headers):
    url = "/api/v1/products/"

    payload = {
        "sku": "LAP-002",
        "name": "Laptop Gamer",
        "price": 2500.0,
        "cost": 1500.0,
        "stock": 5,
        "tax_rate": 21.0,
        "tenant_id": 1
    }

    # 1. Crear producto
    res = client.post(url, json=payload, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["sku"] == "LAP-002"
    assert data["tenant_id"] == 1

    # 2. Listar productos
    res = client.get(url, headers=admin_headers)
    assert res.status_code == 200
    assert len(res.json()) > 0

    # 3. Validar seguridad de Tenant
    payload_intruso = payload.copy()
    payload_intruso["tenant_id"] = 2
    payload_intruso["sku"] = "LAP-003"  # Cambiar SKU para evitar duplicado
    res = client.post(url, json=payload_intruso, headers=admin_headers)
    assert res.status_code == 403


# --- TESTS DE CLIENTES ---
def test_client_full_coverage(client, admin_headers):
    payload = {
        "full_name": "Consultora Tech S.A.",
        "tax_id_type_id": 1,
        "tax_id": "30-22222222-3",
        "tax_responsibility_id": 1,
        "tenant_id": 1,
        "email": "contacto@tech.com"
    }

    # 1. Crear Cliente
    res = client.post("/api/v1/clients/", json=payload, headers=admin_headers)
    assert res.status_code in [200, 201]
    assert res.json()["full_name"] == "Consultora Tech S.A."

    # 2. Verificar duplicado
    res = client.post("/api/v1/clients/", json=payload, headers=admin_headers)
    assert res.status_code == 400


def test_pos_management(client, admin_headers):
    url = "/api/v1/config/pos"

    # 1. Crear un Punto de Venta (usando "code" en lugar de "number")
    pos_payload = {
        "code": "POS-TEST-001",
        "name": "Caja Central Test",
        "tenant_id": 1,
        "is_active": True
    }
    res = client.post(url, json=pos_payload, headers=admin_headers)
    assert res.status_code in [200, 201]

    # 2. Listar mis Puntos de Venta
    res = client.get(url, headers=admin_headers)
    assert res.status_code == 200
    assert any(p["name"] == "Caja Central Test" for p in res.json())


def test_tenant_not_found(client, superadmin_headers):
    # Caso: Buscar un Tenant que no existe
    res = client.get("/api/v1/tenants/999", headers=superadmin_headers)
    assert res.status_code == 404