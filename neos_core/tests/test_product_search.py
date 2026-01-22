from neos_core.database import models


def test_search_products_by_relevance_and_tenant(client, admin_headers, db):
    url = "/api/v1/products/"

    products = [
        {
            "sku": "LAP-100",
            "name": "Laptop Pro",
            "price": 3000.0,
            "cost": 2000.0,
            "stock": 3,
            "tax_rate": 21.0,
            "tenant_id": 1
        },
        {
            "sku": "CAB-200",
            "name": "Cable HDMI",
            "description": "Cable para laptop y monitor",
            "price": 25.0,
            "cost": 10.0,
            "stock": 10,
            "tax_rate": 21.0,
            "tenant_id": 1
        }
    ]

    for payload in products:
        response = client.post(url, json=payload, headers=admin_headers)
        assert response.status_code == 201

    other_tenant_product = models.Product(
        tenant_id=2,
        sku="LAP-999",
        name="Laptop Oculta",
        description="No debería aparecer",
        price=999.0,
        cost=500.0,
        stock=2,
        tax_rate=21.0
    )
    db.add(other_tenant_product)
    db.commit()

    response = client.get("/api/v1/products/search", params={"query": "laptop"}, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert [item["name"] for item in data] == ["Laptop Pro", "Cable HDMI"]

    response = client.get(
        "/api/v1/products/search",
        params={"query": "laptop", "skip": 1, "limit": 1},
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Cable HDMI"
