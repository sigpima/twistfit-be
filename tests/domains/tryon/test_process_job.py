from app.domains.auth import service as auth_service
from app.domains.taxonomy.schemas import TaxonomyGroupInput, TaxonomyValueInput
from app.domains.taxonomy import service as taxonomy_service
from app.domains.tryon import service as tryon_service
from app.domains.tryon.models import TryOnJob, TryOnJobItem
from app.domains.wardrobe import service as wardrobe_service
from app.domains.wardrobe.schemas import WardrobeItemCreate


def _seed_taxonomy(db_session):
    clothing_type = taxonomy_service.create_group(db_session, TaxonomyGroupInput(key="clothing-type", label="Loại quần áo"))
    for key, label in [("ao", "Áo"), ("quan", "Quần"), ("vay", "Váy"), ("dam", "Đầm"), ("ao-khoac", "Áo khoác")]:
        taxonomy_service.create_value(db_session, clothing_type.id, TaxonomyValueInput(key=key, label=label))

    style = taxonomy_service.create_group(db_session, TaxonomyGroupInput(key="style", label="Loại phong cách"))
    for key, label in [("casual", "Casual"), ("formal", "Formal")]:
        taxonomy_service.create_value(db_session, style.id, TaxonomyValueInput(key=key, label=label))

    occasion = taxonomy_service.create_group(db_session, TaxonomyGroupInput(key="occasion", label="Loại dịp"))
    for key, label in [("hang-ngay", "Hằng ngày"), ("du-tiec", "Dự tiệc")]:
        taxonomy_service.create_value(db_session, occasion.id, TaxonomyValueInput(key=key, label=label))


def _create_item(db_session, user_id, category, style="casual", occasion="hang-ngay", colors=None):
    return wardrobe_service.create_item(
        db_session,
        user_id,
        WardrobeItemCreate(
            blob_url=f"https://example.com/{category}.png",
            attributes={"clothing-type": [category], "style": [style], "occasion": [occasion]},
            dominant_colors=colors or ["#F2A93B"],
        ),
    )


def _stub_common(monkeypatch, catvton_batch_fn):
    monkeypatch.setattr(tryon_service, "ensure_container", lambda container: None)
    monkeypatch.setattr(tryon_service, "download_bytes_from_url", lambda url: f"person-bytes:{url}".encode())
    monkeypatch.setattr(tryon_service, "call_catvton_service_batch", catvton_batch_fn)
    monkeypatch.setattr(
        tryon_service, "upload_bytes", lambda container, path, data, content_type="image/png": f"https://example.com/{path}"
    )


def _recording_catvton_batch(calls: list[tuple[list[bytes], bytes, str]]):
    def fake(person_bytes_list, garment_bytes, cloth_type):
        calls.append((person_bytes_list, garment_bytes, cloth_type))
        return [f"result-after-call-{len(calls)}-{i}".encode() for i in range(len(person_bytes_list))]

    return fake


def test_process_job_completes_with_a_single_dress_item(db_session, monkeypatch):
    _seed_taxonomy(db_session)
    user = auth_service.create_user(db_session, name="Test", email="process-job@example.com", password="password123")
    _create_item(db_session, user.id, "dam")
    job = tryon_service.create_job(db_session, user.id, catalog_model_id=1, occasion="hang-ngay", style=None)

    ensured_containers = []
    _stub_common(monkeypatch, lambda persons, garment, cloth_type: [b"result-bytes"] * len(persons))
    monkeypatch.setattr(tryon_service, "ensure_container", ensured_containers.append)

    tryon_service.process_job(
        db_session,
        job.id,
        season="spring",
        front_image_url="https://example.com/model-front.png",
        side_image_url="https://example.com/model-side.png",
    )

    updated = db_session.get(TryOnJob, job.id)
    assert updated.status == "done"
    assert updated.result_front_blob_url is not None
    assert updated.result_side_blob_url is not None
    assert updated.wardrobe_item_id is not None
    assert ensured_containers == ["results"]


def test_process_job_leaves_the_side_result_null_when_no_side_image_is_given(db_session, monkeypatch):
    _seed_taxonomy(db_session)
    user = auth_service.create_user(db_session, name="Test", email="process-job-no-side@example.com", password="password123")
    _create_item(db_session, user.id, "dam")
    job = tryon_service.create_job(db_session, user.id, catalog_model_id=1, occasion="hang-ngay", style=None)

    _stub_common(monkeypatch, lambda persons, garment, cloth_type: [b"result-bytes"] * len(persons))

    tryon_service.process_job(
        db_session, job.id, season="spring", front_image_url="https://example.com/model-front.png"
    )

    updated = db_session.get(TryOnJob, job.id)
    assert updated.status == "done"
    assert updated.result_front_blob_url is not None
    assert updated.result_side_blob_url is None


def test_process_job_chains_shirt_then_pants_batching_both_angles_per_step(db_session, monkeypatch):
    _seed_taxonomy(db_session)
    user = auth_service.create_user(db_session, name="Test", email="process-job-chain@example.com", password="password123")
    _create_item(db_session, user.id, "ao")
    _create_item(db_session, user.id, "quan")
    job = tryon_service.create_job(db_session, user.id, catalog_model_id=1, occasion="hang-ngay", style=None)

    calls: list[tuple[list[bytes], bytes, str]] = []
    _stub_common(monkeypatch, _recording_catvton_batch(calls))

    tryon_service.process_job(
        db_session,
        job.id,
        season="spring",
        front_image_url="https://example.com/model-front.png",
        side_image_url="https://example.com/model-side.png",
    )

    updated = db_session.get(TryOnJob, job.id)
    assert updated.status == "done"
    # One call per combo item, each batching both angles together — not one call per angle.
    assert len(calls) == 2
    assert calls[0][0] == [
        b"person-bytes:https://example.com/model-front.png",
        b"person-bytes:https://example.com/model-side.png",
    ]
    assert calls[0][1] == b"person-bytes:https://example.com/ao.png"  # shirt garment applied first
    assert calls[0][2] == "upper"
    assert calls[1][1] == b"person-bytes:https://example.com/quan.png"  # then pants
    assert calls[1][2] == "lower"
    # The pants call's "person" batch is the shirt call's output batch — a real chain.
    assert calls[1][0] == [b"result-after-call-1-0", b"result-after-call-1-1"]


def test_process_job_chains_jacket_last_over_a_dress(db_session, monkeypatch):
    _seed_taxonomy(db_session)
    user = auth_service.create_user(db_session, name="Test", email="process-job-jacket-dress@example.com", password="password123")
    _create_item(db_session, user.id, "dam")
    _create_item(db_session, user.id, "ao-khoac")
    job = tryon_service.create_job(db_session, user.id, catalog_model_id=1, occasion="hang-ngay", style=None)

    calls: list[tuple[list[bytes], bytes, str]] = []
    _stub_common(monkeypatch, _recording_catvton_batch(calls))

    tryon_service.process_job(db_session, job.id, season="spring", front_image_url="https://example.com/model.png")

    assert db_session.get(TryOnJob, job.id).status == "done"
    assert len(calls) == 2
    assert calls[0][1] == b"person-bytes:https://example.com/dam.png"
    assert calls[0][2] == "overall"
    assert calls[1][1] == b"person-bytes:https://example.com/ao-khoac.png"
    assert calls[1][2] == "upper"


def test_process_job_chains_jacket_last_over_shirt_and_pants(db_session, monkeypatch):
    _seed_taxonomy(db_session)
    user = auth_service.create_user(db_session, name="Test", email="process-job-jacket-full@example.com", password="password123")
    _create_item(db_session, user.id, "ao")
    _create_item(db_session, user.id, "quan")
    _create_item(db_session, user.id, "ao-khoac")
    job = tryon_service.create_job(db_session, user.id, catalog_model_id=1, occasion="hang-ngay", style=None)

    calls: list[tuple[list[bytes], bytes, str]] = []
    _stub_common(monkeypatch, _recording_catvton_batch(calls))

    tryon_service.process_job(db_session, job.id, season="spring", front_image_url="https://example.com/model.png")

    assert db_session.get(TryOnJob, job.id).status == "done"
    assert len(calls) == 3
    assert [call[1] for call in calls] == [
        b"person-bytes:https://example.com/ao.png",
        b"person-bytes:https://example.com/quan.png",
        b"person-bytes:https://example.com/ao-khoac.png",
    ]
    assert [call[2] for call in calls] == ["upper", "lower", "upper"]


def test_process_job_records_every_item_used_in_the_combo_in_order(db_session, monkeypatch):
    _seed_taxonomy(db_session)
    user = auth_service.create_user(db_session, name="Test", email="process-job-items@example.com", password="password123")
    shirt = _create_item(db_session, user.id, "ao")
    pants = _create_item(db_session, user.id, "quan")
    job = tryon_service.create_job(db_session, user.id, catalog_model_id=1, occasion="hang-ngay", style=None)

    _stub_common(monkeypatch, lambda persons, garment, cloth_type: [b"result-bytes"] * len(persons))

    tryon_service.process_job(db_session, job.id, season="spring", front_image_url="https://example.com/model.png")

    items = (
        db_session.query(TryOnJobItem)
        .filter(TryOnJobItem.tryon_job_id == job.id)
        .order_by(TryOnJobItem.sort_order)
        .all()
    )
    assert [item.wardrobe_item_id for item in items] == [shirt.id, pants.id]
    assert [item.sort_order for item in items] == [0, 1]


def test_process_job_matches_by_style_alone_ignoring_the_items_occasion_tag(db_session, monkeypatch):
    _seed_taxonomy(db_session)
    user = auth_service.create_user(db_session, name="Test", email="process-job-style-only@example.com", password="password123")
    # Tagged for a party (occasion=du-tiec), not "hang-ngay" — a style-mode job must still
    # match this on style alone, without also requiring occasion to line up.
    _create_item(db_session, user.id, "dam", style="formal", occasion="du-tiec")
    job = tryon_service.create_job(db_session, user.id, catalog_model_id=1, occasion=None, style="formal")

    _stub_common(monkeypatch, lambda persons, garment, cloth_type: [b"result-bytes"] * len(persons))

    tryon_service.process_job(db_session, job.id, season="spring", front_image_url="https://example.com/model.png")

    updated = db_session.get(TryOnJob, job.id)
    assert updated.status == "done"
    assert updated.wardrobe_item_id is not None


def test_process_job_marks_failed_when_no_matching_item_exists(db_session):
    user = auth_service.create_user(db_session, name="Test", email="process-job-2@example.com", password="password123")
    job = tryon_service.create_job(db_session, user.id, catalog_model_id=1, occasion="du-tiec", style=None)

    tryon_service.process_job(db_session, job.id, season="spring", front_image_url="https://example.com/model.png")

    updated = db_session.get(TryOnJob, job.id)
    assert updated.status == "failed"
    assert updated.error_message == "Không tìm thấy món đồ phù hợp trong tủ đồ cho dịp/phong cách này"


def test_process_job_fails_with_a_not_enough_items_message_when_only_a_shirt_matches(db_session):
    _seed_taxonomy(db_session)
    user = auth_service.create_user(db_session, name="Test", email="process-job-lone-shirt@example.com", password="password123")
    _create_item(db_session, user.id, "ao")
    job = tryon_service.create_job(db_session, user.id, catalog_model_id=1, occasion="hang-ngay", style=None)

    tryon_service.process_job(db_session, job.id, season="spring", front_image_url="https://example.com/model.png")

    updated = db_session.get(TryOnJob, job.id)
    assert updated.status == "failed"
    assert updated.error_message == "Tủ đồ chưa đủ trang phục để ghép thành 1 bộ hoàn chỉnh cho dịp/phong cách này"


def test_process_job_fails_with_a_not_enough_items_message_when_only_a_jacket_matches(db_session):
    _seed_taxonomy(db_session)
    user = auth_service.create_user(db_session, name="Test", email="process-job-lone-jacket@example.com", password="password123")
    _create_item(db_session, user.id, "ao-khoac")
    job = tryon_service.create_job(db_session, user.id, catalog_model_id=1, occasion="hang-ngay", style=None)

    tryon_service.process_job(db_session, job.id, season="spring", front_image_url="https://example.com/model.png")

    updated = db_session.get(TryOnJob, job.id)
    assert updated.status == "failed"
    assert updated.error_message == "Tủ đồ chưa đủ trang phục để ghép thành 1 bộ hoàn chỉnh cho dịp/phong cách này"
