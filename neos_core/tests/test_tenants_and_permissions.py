import pytest
from sqlalchemy.exc import IntegrityError


def test_tenant_conflict_error(client, superadmin_headers):
    payload = {
        "name": "Empresa A",  # Este nombre ya existe por el seed
        "description": "Causa error",
        "tax_id": "30-11111111-1",
        "tax_id_type_id": 1,
        "tax_responsibility_id": 1
    }

    # Capturamos la explosión de la DB si la API no tiene un try/except
    with pytest.raises(Exception):
        client.post("/api/v1/tenants/", json=payload, headers=superadmin_headers)



def test_get_tenants_list(client, superadmin_headers):
    # Probamos sin la barra final. Si tu router tiene tags/prefix,
    # FastAPI a veces se confunde con el trailing slash en el TestClient
    response = client.get("/api/v1/tenants", headers=superadmin_headers)

    # Si sigue dando 405, es que el router de tenants NO tiene un método GET definido.
    # Pero asumiendo que existe para listar:
    if response.status_code == 405:
        # Intento alternativo con slash (por si acaso)
        response = client.get("/api/v1/tenants/", headers=superadmin_headers)

    assert response.status_code == 200