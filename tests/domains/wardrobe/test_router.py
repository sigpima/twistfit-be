from app.domains.taxonomy.schemas import TaxonomyGroupInput, TaxonomyValueInput
from app.domains.taxonomy import service as taxonomy_service


def _login(client, email: str):
    client.post("/auth/register", json={"name": "Test", "identifier": email, "password": "password123"})
    client.post("/auth/login", json={"identifier": email, "password": "password123"})


def _seed_clothing_type_group(db_session):
    group = taxonomy_service.create_group(db_session, TaxonomyGroupInput(key="clothing-type", label="Loại quần áo"))
    taxonomy_service.create_value(db_session, group.id, TaxonomyValueInput(key="ao", label="Áo"))
    return group


def test_create_item_requires_authentication(client):
    response = client.post(
        "/wardrobe/items",
        json={
            "blobUrl": "https://example.com/a.png",
            "attributes": {"clothing-type": ["ao"]},
            "dominantColors": ["#ff0000"],
        },
    )
    assert response.status_code == 401


def test_create_and_list_items(client, db_session):
    _seed_clothing_type_group(db_session)
    _login(client, "wardrobe-router@example.com")

    create_response = client.post(
        "/wardrobe/items",
        json={
            "blobUrl": "https://example.com/a.png",
            "attributes": {"clothing-type": ["ao"]},
            "dominantColors": ["#ff0000"],
        },
    )
    assert create_response.status_code == 201

    list_response = client.get("/wardrobe/items")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_create_item_rejects_an_invalid_category(client, db_session):
    _seed_clothing_type_group(db_session)
    _login(client, "wardrobe-router-2@example.com")

    response = client.post(
        "/wardrobe/items",
        json={
            "blobUrl": "https://example.com/a.png",
            "attributes": {"clothing-type": ["not-a-real-category"]},
            "dominantColors": ["#ff0000"],
        },
    )
    assert response.status_code == 400
