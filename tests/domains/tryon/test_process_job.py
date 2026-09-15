import pytest

from app.domains.auth import service as auth_service
from app.domains.tryon import service as tryon_service
from app.domains.tryon.models import TryOnJob
from app.domains.wardrobe import service as wardrobe_service
from app.domains.wardrobe.schemas import WardrobeItemCreate


def test_process_job_completes_successfully(db_session, monkeypatch):
    user = auth_service.create_user(db_session, name="Test", email="process-job@example.com", password="password123")
    wardrobe_service.create_item(
        db_session,
        user.id,
        WardrobeItemCreate(
            blob_url="https://example.com/garment.png",
            category="ao-thun",
            style_tags=["casual"],
            occasion_tags=["hang-ngay"],
            dominant_colors=["#F2A93B"],
        ),
    )
    job = tryon_service.create_job(db_session, user.id, catalog_model_id=1, occasion="hang-ngay", style="casual")

    ensured_containers = []
    monkeypatch.setattr(tryon_service, "ensure_container", ensured_containers.append)
    monkeypatch.setattr(tryon_service, "download_bytes_from_url", lambda url: b"fake-image-bytes")
    monkeypatch.setattr(tryon_service, "call_catvton_service", lambda person, garment, cloth_type: b"result-bytes")
    monkeypatch.setattr(tryon_service, "upload_bytes", lambda container, path, data, content_type="image/png": "https://example.com/results/1.png")

    tryon_service.process_job(db_session, job.id, season="spring", catalog_model_image_url="https://example.com/model.png")

    updated = db_session.get(TryOnJob, job.id)
    assert updated.status == "done"
    assert updated.result_blob_url == "https://example.com/results/1.png"
    assert updated.wardrobe_item_id is not None
    assert ensured_containers == ["results"]


@pytest.mark.parametrize(
    "category,expected_cloth_type",
    [
        ("ao-thun", "upper"),
        ("ao-so-mi", "upper"),
        ("ao-khoac", "upper"),
        ("quan-jean", "lower"),
        ("dam", "overall"),
    ],
)
def test_process_job_passes_the_cloth_type_matching_the_garment_category(
    db_session, monkeypatch, category, expected_cloth_type
):
    user = auth_service.create_user(db_session, name="Test", email=f"cloth-type-{category}@example.com", password="password123")
    wardrobe_service.create_item(
        db_session,
        user.id,
        WardrobeItemCreate(
            blob_url="https://example.com/garment.png",
            category=category,
            style_tags=["casual"],
            occasion_tags=["hang-ngay"],
            dominant_colors=["#F2A93B"],
        ),
    )
    job = tryon_service.create_job(db_session, user.id, catalog_model_id=1, occasion="hang-ngay", style="casual")

    captured = {}
    monkeypatch.setattr(tryon_service, "ensure_container", lambda container: None)
    monkeypatch.setattr(tryon_service, "download_bytes_from_url", lambda url: b"fake-image-bytes")

    def fake_call_catvton_service(person_bytes, garment_bytes, cloth_type):
        captured["cloth_type"] = cloth_type
        return b"result-bytes"

    monkeypatch.setattr(tryon_service, "call_catvton_service", fake_call_catvton_service)
    monkeypatch.setattr(tryon_service, "upload_bytes", lambda container, path, data, content_type="image/png": "https://example.com/results/1.png")

    tryon_service.process_job(db_session, job.id, season="spring", catalog_model_image_url="https://example.com/model.png")

    assert captured["cloth_type"] == expected_cloth_type


def test_process_job_marks_failed_when_no_matching_item_exists(db_session):
    user = auth_service.create_user(db_session, name="Test", email="process-job-2@example.com", password="password123")
    job = tryon_service.create_job(db_session, user.id, catalog_model_id=1, occasion="du-tiec", style="formal")

    tryon_service.process_job(db_session, job.id, season="spring", catalog_model_image_url="https://example.com/model.png")

    updated = db_session.get(TryOnJob, job.id)
    assert updated.status == "failed"
    assert updated.error_message is not None
