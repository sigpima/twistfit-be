from app.core.security import hash_password
from app.domains.auth.models import User
from app.domains.tryon.models import TryOnJob


def test_create_tryon_job(db_session):
    user = User(name="Test", email="tryon-model@example.com", password_hash=hash_password("password123"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    job = TryOnJob(
        user_id=user.id,
        catalog_model_id=1,
        occasion="hang-ngay",
        style="casual",
        status="pending",
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    assert job.id is not None
    assert job.status == "pending"
    assert job.wardrobe_item_id is None
    assert job.result_front_blob_url is None
    assert job.result_side_blob_url is None
