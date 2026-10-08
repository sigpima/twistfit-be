from app.domains.taxonomy.schemas import TaxonomyGroupInput, TaxonomyValueInput
from app.domains.taxonomy import service as taxonomy_service


def _login(client, email: str):
    client.post("/auth/register", json={"name": "Test", "identifier": email, "password": "password123"})
    client.post("/auth/login", json={"identifier": email, "password": "password123"})


def _seed_clothing_type_group(db_session):
    group = taxonomy_service.create_group(db_session, TaxonomyGroupInput(key="clothing-type", label="Loại quần áo"))
    taxonomy_service.create_value(db_session, group.id, TaxonomyValueInput(key="ao", label="Áo"))
    return group


def _seed_required_groups(db_session):
    _seed_clothing_type_group(db_session)
    occasion = taxonomy_service.create_group(db_session, TaxonomyGroupInput(key="occasion", label="Dịp"))
    taxonomy_service.create_value(db_session, occasion.id, TaxonomyValueInput(key="hang-ngay", label="Hằng ngày"))
    style = taxonomy_service.create_group(db_session, TaxonomyGroupInput(key="style", label="Phong cách"))
    taxonomy_service.create_value(db_session, style.id, TaxonomyValueInput(key="casual", label="Casual"))


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
    _seed_required_groups(db_session)
    _login(client, "wardrobe-router@example.com")

    create_response = client.post(
        "/wardrobe/items",
        json={
            "blobUrl": "https://example.com/a.png",
            "attributes": {"clothing-type": ["ao"], "occasion": ["hang-ngay"], "style": ["casual"]},
            "dominantColors": ["#ff0000"],
        },
    )
    assert create_response.status_code == 201

    list_response = client.get("/wardrobe/items")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_delete_item_removes_it(client, db_session):
    _seed_required_groups(db_session)
    _login(client, "wardrobe-router-delete-1@example.com")
    create_response = client.post(
        "/wardrobe/items",
        json={
            "blobUrl": "https://example.com/a.png",
            "attributes": {"clothing-type": ["ao"], "occasion": ["hang-ngay"], "style": ["casual"]},
            "dominantColors": ["#ff0000"],
        },
    )
    item_id = create_response.json()["id"]

    delete_response = client.delete(f"/wardrobe/items/{item_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/wardrobe/items/{item_id}")
    assert get_response.status_code == 404


def test_delete_item_requires_authentication(client):
    response = client.delete("/wardrobe/items/1")
    assert response.status_code == 401


def test_delete_item_404s_for_an_item_that_does_not_exist(client):
    _login(client, "wardrobe-router-delete-2@example.com")
    response = client.delete("/wardrobe/items/999999")
    assert response.status_code == 404


def test_delete_item_404s_for_another_users_item(client, db_session):
    _seed_required_groups(db_session)
    _login(client, "wardrobe-router-delete-3@example.com")
    create_response = client.post(
        "/wardrobe/items",
        json={
            "blobUrl": "https://example.com/a.png",
            "attributes": {"clothing-type": ["ao"], "occasion": ["hang-ngay"], "style": ["casual"]},
            "dominantColors": ["#ff0000"],
        },
    )
    item_id = create_response.json()["id"]

    client.post("/auth/logout")
    _login(client, "wardrobe-router-delete-4@example.com")

    response = client.delete(f"/wardrobe/items/{item_id}")
    assert response.status_code == 404


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
