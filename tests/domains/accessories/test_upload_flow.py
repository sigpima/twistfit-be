import io
import uuid

from PIL import Image

from app.core.blob_storage import ensure_container, upload_bytes
from app.domains.accessories import router as accessories_router


def _promote_to_admin(db_session, email: str) -> None:
    from app.domains.auth.models import User

    db_session.query(User).filter(User.email == email).update({"role": "admin"})
    db_session.commit()


def _login_as_admin(client, db_session, email: str) -> None:
    client.post("/auth/register", json={"name": "Admin", "identifier": email, "password": "password123"})
    _promote_to_admin(db_session, email)
    client.post("/auth/login", json={"identifier": email, "password": "password123"})


def test_upload_url_requires_admin(client):
    response = client.post("/accessories/upload-url")
    assert response.status_code == 401


def test_upload_url_returns_a_writable_sas_url(client, db_session):
    _login_as_admin(client, db_session, "accessory-upload@example.com")

    response = client.post("/accessories/upload-url")

    assert response.status_code == 200
    body = response.json()
    assert "uploadUrl" in body
    assert "X-Amz-Signature=" in body["uploadUrl"]
    assert "blobPath" in body


def test_suggest_tags_returns_the_gemini_result_and_blob_url(client, db_session, monkeypatch):
    _login_as_admin(client, db_session, "accessory-suggest@example.com")

    ensure_container("accessories")
    blob_path = f"{uuid.uuid4()}.png"
    buffer = io.BytesIO()
    Image.new("RGB", (16, 16), (255, 0, 0)).save(buffer, format="PNG")
    upload_bytes("accessories", blob_path, buffer.getvalue())

    # Patch the name as bound in the router module (where `from
    # gemini_client import suggest_tags` copied the reference at import
    # time) — patching gemini_client.suggest_tags itself wouldn't affect
    # what the router already imported.
    monkeypatch.setattr(
        accessories_router,
        "suggest_tags",
        lambda image_bytes, db: {
            "category": "tui-xach",
            "styleTags": ["casual"],
            "occasionTags": ["hang-ngay"],
            "toneTags": ["autumn"],
        },
    )

    response = client.post("/accessories/suggest-tags", json={"blobPath": blob_path})

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "tui-xach"
    assert body["toneTags"] == ["autumn"]
    assert blob_path in body["blobUrl"]


def test_suggest_tags_falls_back_to_empty_tags_when_gemini_fails(client, db_session, monkeypatch):
    # Gemini is a third-party call that can fail (rate limit, outage,
    # malformed response) independently of the upload itself — the admin
    # must still get the image back to tag by hand rather than a dead end.
    _login_as_admin(client, db_session, "accessory-suggest-2@example.com")

    ensure_container("accessories")
    blob_path = f"{uuid.uuid4()}.png"
    buffer = io.BytesIO()
    Image.new("RGB", (16, 16), (255, 0, 0)).save(buffer, format="PNG")
    upload_bytes("accessories", blob_path, buffer.getvalue())

    def _raise(image_bytes, db):
        raise ValueError("Gemini returned malformed JSON")

    monkeypatch.setattr(accessories_router, "suggest_tags", _raise)

    response = client.post("/accessories/suggest-tags", json={"blobPath": blob_path})

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "tui-xach"
    assert body["styleTags"] == []
    assert body["occasionTags"] == []
    assert body["toneTags"] == []
    assert blob_path in body["blobUrl"]
