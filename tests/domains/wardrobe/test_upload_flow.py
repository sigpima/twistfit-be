import uuid

from app.core.blob_storage import ensure_container, upload_bytes
from app.domains.wardrobe import router as wardrobe_router


def _login(client, email: str):
    client.post("/auth/register", json={"name": "Test", "identifier": email, "password": "password123"})
    client.post("/auth/login", json={"identifier": email, "password": "password123"})


def test_upload_url_requires_authentication(client):
    response = client.post("/wardrobe/upload-url")
    assert response.status_code == 401


def test_upload_url_returns_a_writable_sas_url(client):
    _login(client, "wardrobe-upload@example.com")

    response = client.post("/wardrobe/upload-url")

    assert response.status_code == 200
    body = response.json()
    assert "uploadUrl" in body
    assert "X-Amz-Signature=" in body["uploadUrl"]
    assert "blobPath" in body


def test_suggest_tags_combines_gemini_and_color_extraction(client, monkeypatch):
    _login(client, "wardrobe-suggest@example.com")

    ensure_container("wardrobe")
    blob_path = f"{uuid.uuid4()}.png"
    import io

    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (16, 16), (255, 0, 0)).save(buffer, format="PNG")
    upload_bytes("wardrobe", blob_path, buffer.getvalue())

    monkeypatch.setattr(
        wardrobe_router,
        "suggest_tags",
        lambda image_bytes, db: {"clothing-type": ["ao"], "style": ["casual"], "occasion": ["hang-ngay"]},
    )

    response = client.post("/wardrobe/items/suggest-tags", json={"blobPath": blob_path})

    assert response.status_code == 200
    body = response.json()
    assert body["clothing-type"] == ["ao"]
    assert body["dominantColors"] == ["#ff0000"]
    assert blob_path in body["blobUrl"]


def test_suggest_tags_falls_back_to_no_suggested_attributes_when_gemini_fails(client, monkeypatch):
    _login(client, "wardrobe-suggest-fallback@example.com")

    ensure_container("wardrobe")
    blob_path = f"{uuid.uuid4()}.png"
    import io

    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (16, 16), (0, 255, 0)).save(buffer, format="PNG")
    upload_bytes("wardrobe", blob_path, buffer.getvalue())

    def _raise(image_bytes, db):
        raise RuntimeError("Gemini is down")

    monkeypatch.setattr(wardrobe_router, "suggest_tags", _raise)

    response = client.post("/wardrobe/items/suggest-tags", json={"blobPath": blob_path})

    # Still 200 — Gemini failing must degrade to "no suggestion", not block
    # the user from reaching the review step and tagging by hand.
    assert response.status_code == 200
    body = response.json()
    assert body.get("clothing-type", []) == []
    assert body.get("occasion", []) == []
    assert body.get("style", []) == []
    assert body["dominantColors"] == ["#00ff00"]
    assert blob_path in body["blobUrl"]
