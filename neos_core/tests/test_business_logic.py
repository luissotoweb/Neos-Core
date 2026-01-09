import pytest


# --- TESTS DE INVENTARIO ---
def test_inventory_full_coverage(client, admin_headers):
    # CORRECCIÓN 1: La URL correcta suele ser la raíz del prefijo "/inventory/"
    # Si antes usábamos "/products" y daba 404, es porque la ruta está definida en "/"
    url = "/api/v1/products/"

    payload = {
        "sku": "LAP-002",
        "name": "Laptop Gamer",
        "price": 2500.0,
        "stock": 5,  # Asegúrate de usar "stock" (según tu schema)
        "tenant_id": 1
        # Nota: Eliminamos category_id para evitar errores si no hay categorías creadas
    }

    # 1. Crear producto
    res = client.post(url, json=payload, headers=admin_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["sku"] == "LAP-002"
    assert data["tenant_id"] == 1

    # 2. Listar productos (Cubre el GET)
    res = client.get(url, headers=admin_headers)
    assert res.status_code == 200
    assert len(res.json()) > 0

    # 3. Validar seguridad de Tenant (Intento crear para tenant 2 con token de tenant 1)
    payload_intruso = payload.copy()
    payload_intruso["tenant_id"] = 2
    res = client.post(url, json=payload_intruso, headers=admin_headers)
    assert res.status_code == 403


# --- TESTS DE CLIENTES ---
def test_client_full_coverage(client, admin_headers):
    # CORRECCIÓN 2: Eliminamos el campo "phone" que causaba el TypeError
    # Solo enviamos lo que el modelo ClientModel realmente tiene.
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
    # Aceptamos 200 o 201 según cómo esté tu return en el router
    assert res.status_code in [200, 201]
    assert res.json()["full_name"] == "Consultora Tech S.A."

    # 2. Verificar duplicado (Debe fallar con 400 porque el tax_id es el mismo)
    res = client.post("/api/v1/clients/", json=payload, headers=admin_headers)
    assert res.status_code == 400


def test_pos_management(client, admin_headers):
    url = "/api/v1/config/pos"

    # 1. Crear un Punto de Venta
    pos_payload = {
        "number": 1,
        "name": "Caja Central",
        "tenant_id": 1
    }
    res = client.post(url, json=pos_payload, headers=admin_headers)
    assert res.status_code == 200

    # 2. Listar mis Puntos de Venta
    res = client.get(url, headers=admin_headers)
    assert res.status_code == 200
    assert any(p["name"] == "Caja Central" for p in res.json())


def test_tenant_not_found(client, superadmin_headers):
    # Caso: Buscar un Tenant que no existe (Cubre el 404 de tenant_routes)
    res = client.get("/api/v1/tenants/999", headers=superadmin_headers)
    assert res.status_code == 404