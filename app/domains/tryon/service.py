from sqlalchemy.orm import Session

from app.core.blob_storage import download_bytes_from_url, ensure_container, upload_bytes
from app.domains.tryon.catvton_client import call_catvton_service
from app.domains.tryon.garment_selection import select_best_matching_item
from app.domains.tryon.models import TryOnJob
from app.domains.wardrobe.models import WardrobeItem


def create_job(
    db: Session, user_id: int, catalog_model_id: int, occasion: str, style: str, pose: str = "front"
) -> TryOnJob:
    job = TryOnJob(
        user_id=user_id,
        catalog_model_id=catalog_model_id,
        occasion=occasion,
        style=style,
        pose=pose,
        status="pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, user_id: int, job_id: int) -> TryOnJob | None:
    return db.query(TryOnJob).filter(TryOnJob.id == job_id, TryOnJob.user_id == user_id).first()


def process_job(db: Session, job_id: int, season: str, catalog_model_image_url: str) -> None:
    job = db.get(TryOnJob, job_id)
    if job is None:
        return

    job.status = "processing"
    db.commit()

    try:
        candidates = (
            db.query(WardrobeItem)
            .filter(
                WardrobeItem.user_id == job.user_id,
                WardrobeItem.occasion_tags.contains([job.occasion]),
                WardrobeItem.style_tags.contains([job.style]),
            )
            .all()
        )
        selected = select_best_matching_item(candidates, season)
        if selected is None:
            raise ValueError("Không tìm thấy món đồ phù hợp trong tủ đồ cho dịp/phong cách này")

        job.wardrobe_item_id = selected.id
        db.commit()

        garment_bytes = download_bytes_from_url(selected.blob_url)
        person_bytes = download_bytes_from_url(catalog_model_image_url)

        result_bytes = call_catvton_service(person_bytes, garment_bytes, "upper")

        ensure_container("results")
        result_url = upload_bytes("results", f"{job.user_id}/{job.id}.png", result_bytes)

        job.result_blob_url = result_url
        job.status = "done"
        db.commit()
    except Exception as error:  # noqa: BLE001 — any failure here must land the job in `failed`, not crash the background task
        job.status = "failed"
        job.error_message = str(error)
        db.commit()
