from app.domains.model_catalog.models import CatalogModel
from app.domains.tryon import service as tryon_service


def _login(client, email: str):
    client.post("/auth/register", json={"name": "Test", "identifier": email, "password": "password123"})
    client.post("/auth/login", json={"identifier": email, "password": "password123"})


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
    response = client.post("/tryon", json={"catalogModelId": 1, "occasion": "hang-ngay"})
    assert response.status_code == 401


def test_create_job_returns_404_for_an_unknown_catalog_model(client):
    _login(client, "tryon-router@example.com")
    response = client.post("/tryon", json={"catalogModelId": 999999, "occasion": "hang-ngay"})
    assert response.status_code == 404


def test_create_and_fetch_job(client, db_session):
    _login(client, "tryon-router-2@example.com")
    model = _seed_catalog_model(db_session)

    create_response = client.post(
        "/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay"}
    )
    assert create_response.status_code == 201
    job_id = create_response.json()["id"]

    get_response = client.get(f"/tryon/{job_id}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] in ("pending", "processing", "done", "failed")


def test_create_job_rejects_both_occasion_and_style_given_together(client, db_session):
    _login(client, "tryon-both-axes@example.com")
    model = _seed_catalog_model(db_session)
    response = client.post(
        "/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay", "style": "casual"}
    )
    assert response.status_code == 422


def test_create_job_rejects_neither_occasion_nor_style_given(client, db_session):
    _login(client, "tryon-no-axes@example.com")
    model = _seed_catalog_model(db_session)
    response = client.post("/tryon", json={"catalogModelId": model.id})
    assert response.status_code == 422


def test_create_job_accepts_style_alone(client, db_session):
    _login(client, "tryon-style-alone@example.com")
    model = _seed_catalog_model(db_session)
    response = client.post("/tryon", json={"catalogModelId": model.id, "style": "formal"})
    assert response.status_code == 201
    assert response.json()["style"] == "formal"
    assert response.json()["occasion"] is None


def test_list_jobs_requires_authentication(client):
    response = client.get("/tryon")
    assert response.status_code == 401


def test_list_jobs_returns_only_the_current_users_jobs_newest_first(client, db_session):
    _login(client, "tryon-list-1@example.com")
    model = _seed_catalog_model(db_session)
    first = client.post("/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay"})
    second = client.post("/tryon", json={"catalogModelId": model.id, "occasion": "du-tiec"})

    client.post("/auth/logout")
    _login(client, "tryon-list-2@example.com")
    other_job = client.post(
        "/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay"}
    )

    client.post("/auth/logout")
    _login(client, "tryon-list-1@example.com")
    response = client.get("/tryon")

    assert response.status_code == 200
    job_ids = [job["id"] for job in response.json()]
    assert job_ids == [second.json()["id"], first.json()["id"]]
    assert other_job.json()["id"] not in job_ids


def test_list_jobs_returns_an_empty_list_for_a_user_with_no_jobs(client):
    _login(client, "tryon-list-empty@example.com")
    response = client.get("/tryon")
    assert response.status_code == 200
    assert response.json() == []


def test_get_job_404s_for_another_users_job(client, db_session):
    _login(client, "tryon-router-3@example.com")
    model = _seed_catalog_model(db_session)
    create_response = client.post(
        "/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay"}
    )
    job_id = create_response.json()["id"]

    client.post("/auth/logout")
    _login(client, "tryon-router-4@example.com")

    response = client.get(f"/tryon/{job_id}")
    assert response.status_code == 404


def test_delete_job_removes_it(client, db_session):
    _login(client, "tryon-router-delete-1@example.com")
    model = _seed_catalog_model(db_session)
    create_response = client.post("/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay"})
    job_id = create_response.json()["id"]

    delete_response = client.delete(f"/tryon/{job_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/tryon/{job_id}")
    assert get_response.status_code == 404


def test_delete_job_requires_authentication(client):
    response = client.delete("/tryon/1")
    assert response.status_code == 401


def test_delete_job_404s_for_a_job_that_does_not_exist(client):
    _login(client, "tryon-router-delete-2@example.com")
    response = client.delete("/tryon/999999")
    assert response.status_code == 404


def test_delete_job_404s_for_another_users_job(client, db_session):
    _login(client, "tryon-router-delete-3@example.com")
    model = _seed_catalog_model(db_session)
    create_response = client.post("/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay"})
    job_id = create_response.json()["id"]

    client.post("/auth/logout")
    _login(client, "tryon-router-delete-4@example.com")

    response = client.delete(f"/tryon/{job_id}")
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


def test_create_job_resolves_both_the_front_and_side_catalog_model_images(client, db_session, monkeypatch):
    captured = {}
    monkeypatch.setattr(
        tryon_service,
        "process_job",
        lambda db, job_id, season, front_image_url, side_image_url: captured.update(
            front=front_image_url, side=side_image_url
        ),
    )

    _login(client, "tryon-pose-2@example.com")
    model = _seed_catalog_model_with_side_image(db_session)

    response = client.post("/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay"})

    assert response.status_code == 201
    assert captured["front"] == "http://localhost:3000/outfit/models/test-front.jpg"
    assert captured["side"] == "http://localhost:3000/outfit/models/test-side.jpg"


def test_create_job_leaves_the_side_image_null_when_the_model_has_none(client, db_session, monkeypatch):
    captured = {}
    monkeypatch.setattr(
        tryon_service,
        "process_job",
        lambda db, job_id, season, front_image_url, side_image_url: captured.update(
            front=front_image_url, side=side_image_url
        ),
    )

    _login(client, "tryon-pose-3@example.com")
    model = _seed_catalog_model(db_session)

    response = client.post("/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay"})

    assert response.status_code == 201
    assert captured["side"] is None


def test_create_job_resolves_a_relative_catalog_model_image_to_an_absolute_url(client, db_session, monkeypatch):
    captured = {}
    monkeypatch.setattr(
        tryon_service,
        "process_job",
        lambda db, job_id, season, front_image_url, side_image_url: captured.update(url=front_image_url),
    )

    _login(client, "tryon-absolute-url@example.com")
    model = _seed_catalog_model(db_session)
    assert model.image == "/outfit/models/test.jpg"

    response = client.post("/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay"})

    assert response.status_code == 201
    assert captured["url"] == "http://localhost:3000/outfit/models/test.jpg"


def test_create_job_returns_429_once_the_daily_quota_is_exhausted(client, db_session, monkeypatch):
    monkeypatch.setattr(tryon_service, "process_job", lambda *args, **kwargs: None)

    _login(client, "tryon-quota-limit@example.com")
    model = _seed_catalog_model(db_session)

    for _ in range(5):
        response = client.post("/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay"})
        assert response.status_code == 201

    sixth_response = client.post("/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay"})
    assert sixth_response.status_code == 429


def test_create_job_quota_is_scoped_per_user(client, db_session, monkeypatch):
    monkeypatch.setattr(tryon_service, "process_job", lambda *args, **kwargs: None)
    model = _seed_catalog_model(db_session)

    _login(client, "tryon-quota-user-a@example.com")
    for _ in range(5):
        assert client.post("/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay"}).status_code == 201
    assert client.post("/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay"}).status_code == 429

    client.post("/auth/logout")
    _login(client, "tryon-quota-user-b@example.com")
    assert client.post("/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay"}).status_code == 201


def test_get_quota_requires_authentication(client):
    response = client.get("/tryon/quota")
    assert response.status_code == 401


def test_get_quota_reports_used_and_remaining(client, db_session, monkeypatch):
    monkeypatch.setattr(tryon_service, "process_job", lambda *args, **kwargs: None)
    _login(client, "tryon-quota-get@example.com")
    model = _seed_catalog_model(db_session)

    initial = client.get("/tryon/quota")
    assert initial.status_code == 200
    assert initial.json() == {"usedToday": 0, "limit": 5, "remainingToday": 5}

    client.post("/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay"})
    client.post("/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay"})

    after = client.get("/tryon/quota")
    assert after.status_code == 200
    assert after.json() == {"usedToday": 2, "limit": 5, "remainingToday": 3}


def test_create_job_leaves_an_already_absolute_catalog_model_image_untouched(client, db_session, monkeypatch):
    captured = {}
    monkeypatch.setattr(
        tryon_service,
        "process_job",
        lambda db, job_id, season, front_image_url, side_image_url: captured.update(url=front_image_url),
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

    response = client.post("/tryon", json={"catalogModelId": model.id, "occasion": "hang-ngay"})

    assert response.status_code == 201
    assert captured["url"] == "https://cdn.example.com/models/test.jpg"
