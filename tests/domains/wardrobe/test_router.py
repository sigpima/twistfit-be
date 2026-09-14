def _login(client, email: str):
    client.post("/auth/register", json={"name": "Test", "email": email, "password": "password123"})
    client.post("/auth/login", json={"email": email, "password": "password123"})


def test_create_item_requires_authentication(client):
    response = client.post(
        "/wardrobe/items",
        json={
            "blobUrl": "https://example.com/a.png",
            "category": "ao-thun",
            "styleTags": ["casual"],
            "occasionTags": ["hang-ngay"],
            "dominantColors": ["#ff0000"],
        },
    )
    assert response.status_code == 401


def test_create_and_list_items(client):
    _login(client, "wardrobe-router@example.com")

    create_response = client.post(
        "/wardrobe/items",
        json={
            "blobUrl": "https://example.com/a.png",
            "category": "ao-thun",
            "styleTags": ["casual"],
            "occasionTags": ["hang-ngay"],
            "dominantColors": ["#ff0000"],
        },
    )
    assert create_response.status_code == 201

    list_response = client.get("/wardrobe/items")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_create_item_rejects_an_invalid_category(client):
    _login(client, "wardrobe-router-2@example.com")

    response = client.post(
        "/wardrobe/items",
        json={
            "blobUrl": "https://example.com/a.png",
            "category": "not-a-real-category",
            "styleTags": ["casual"],
            "occasionTags": ["hang-ngay"],
            "dominantColors": ["#ff0000"],
        },
    )
    assert response.status_code == 422
