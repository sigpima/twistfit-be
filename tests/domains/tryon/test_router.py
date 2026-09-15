from app.domains.model_catalog.models import CatalogModel
from app.domains.tryon import service as tryon_service


def _login(client, email: str):
    client.post("/auth/register", json={"name": "Test", "email": email, "password": "password123"})
    client.post("/auth/login", json={"email": email, "password": "password123"})


def _seed_catalog_model(db_session) -> CatalogModel:
    model = CatalogModel(
        name="Test Model",
        image="/outfit/models/test.jpg",
        dossier_image="/outfit/models/test.jpg",
        pose_count=1,
        tagline="Test",
        undertone="warm",
        height="1m70",
        body_shape="Test",
        waist="60cm",
        personal_color="Autumn Warm",
    )
    db_session.add(model)
    db_session.commit()
    db_session.refresh(model)
    return model


def test_create_job_requires_authentication(client):
    response = client.post("/tryon", json={"catalogModelId": 1, "occasion": "hang-ngay", "style": "casual"})
    assert response.status_code == 401


def test_create_job_returns_404_for_an_unknown_catalog_model(client):
    _login(client, "tryon-router@example.com")
    response = client.post("/tryon", json={"catalogModelId": 999999, "occasion": "hang-ngay", "style": "casual"})
    assert response.status_code == 404


def test_create_and_fetch_job(client, db_session):
    _login(client, "tryon-router-2@example.com")
    model = _seed_catalog_model(db_session)

    create_response = client.post(
        "/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay", "style": "casual"}
    )
    assert create_response.status_code == 201
    job_id = create_response.json()["id"]

    get_response = client.get(f"/tryon/{job_id}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] in ("pending", "processing", "done", "failed")


def test_get_job_404s_for_another_users_job(client, db_session):
    _login(client, "tryon-router-3@example.com")
    model = _seed_catalog_model(db_session)
    create_response = client.post(
        "/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay", "style": "casual"}
    )
    job_id = create_response.json()["id"]

    client.post("/auth/logout")
    _login(client, "tryon-router-4@example.com")

    response = client.get(f"/tryon/{job_id}")
    assert response.status_code == 404


def _seed_catalog_model_with_side_image(db_session) -> CatalogModel:
    model = CatalogModel(
        name="Test Model",
        image="/outfit/models/test-front.jpg",
        dossier_image="/outfit/models/test-front.jpg",
        side_image="/outfit/models/test-side.jpg",
        pose_count=1,
        tagline="Test",
        undertone="warm",
        height="1m70",
        body_shape="Test",
        waist="60cm",
        personal_color="Autumn Warm",
    )
    db_session.add(model)
    db_session.commit()
    db_session.refresh(model)
    return model


def test_create_job_defaults_pose_to_front(client, db_session):
    _login(client, "tryon-pose-1@example.com")
    model = _seed_catalog_model(db_session)

    response = client.post("/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay", "style": "casual"})

    assert response.status_code == 201
    assert response.json()["pose"] == "front"


def test_create_job_accepts_an_explicit_pose(client, db_session):
    _login(client, "tryon-pose-2@example.com")
    model = _seed_catalog_model_with_side_image(db_session)

    response = client.post(
        "/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay", "style": "casual", "pose": "side"}
    )

    assert response.status_code == 201
    assert response.json()["pose"] == "side"


def test_create_job_rejects_an_invalid_pose(client, db_session):
    _login(client, "tryon-pose-3@example.com")
    model = _seed_catalog_model(db_session)

    response = client.post(
        "/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay", "style": "casual", "pose": "flying"}
    )

    assert response.status_code == 422


def test_create_job_resolves_a_relative_catalog_model_image_to_an_absolute_url(client, db_session, monkeypatch):
    captured = {}
    monkeypatch.setattr(
        tryon_service,
        "process_job",
        lambda db, job_id, season, catalog_model_image_url: captured.update(url=catalog_model_image_url),
    )

    _login(client, "tryon-absolute-url@example.com")
    model = _seed_catalog_model(db_session)
    assert model.image == "/outfit/models/test.jpg"

    response = client.post("/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay", "style": "casual"})

    assert response.status_code == 201
    assert captured["url"] == "http://localhost:3000/outfit/models/test.jpg"


def test_create_job_leaves_an_already_absolute_catalog_model_image_untouched(client, db_session, monkeypatch):
    captured = {}
    monkeypatch.setattr(
        tryon_service,
        "process_job",
        lambda db, job_id, season, catalog_model_image_url: captured.update(url=catalog_model_image_url),
    )

    _login(client, "tryon-absolute-url-2@example.com")
    model = CatalogModel(
        name="Hosted Model",
        image="https://cdn.example.com/models/test.jpg",
        dossier_image="https://cdn.example.com/models/test.jpg",
        pose_count=1,
        tagline="Test",
        undertone="warm",
        height="1m70",
        body_shape="Test",
        waist="60cm",
        personal_color="Autumn Warm",
    )
    db_session.add(model)
    db_session.commit()
    db_session.refresh(model)

    response = client.post("/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay", "style": "casual"})

    assert response.status_code == 201
    assert captured["url"] == "https://cdn.example.com/models/test.jpg"
