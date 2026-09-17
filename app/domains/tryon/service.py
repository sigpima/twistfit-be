from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session

from app.core.blob_storage import download_bytes_from_url, ensure_container, upload_bytes
from app.domains.tryon.catvton_client import call_catvton_service
from app.domains.tryon.garment_selection import select_best_matching_item
from app.domains.tryon.models import TryOnJob
from app.domains.wardrobe.models import WardrobeItem

CLOTH_TYPE_BY_CLOTHING_TYPE = {
    "ao": "upper",
    "ao-khoac": "upper",
    "quan": "lower",
    "vay": "lower",
    "dam": "overall",
}


def create_job(db: Session, user_id: int, catalog_model_id: int, occasion: str, style: str) -> TryOnJob:
    job = TryOnJob(
        user_id=user_id,
        catalog_model_id=catalog_model_id,
        occasion=occasion,
        style=style,
        status="pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, user_id: int, job_id: int) -> TryOnJob | None:
    return db.query(TryOnJob).filter(TryOnJob.id == job_id, TryOnJob.user_id == user_id).first()


def process_job(db: Session, job_id: int, season: str, front_image_url: str, side_image_url: str | None = None) -> None:
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
                cast(WardrobeItem.attributes["occasion"], JSONB).contains([job.occasion]),
                cast(WardrobeItem.attributes["style"], JSONB).contains([job.style]),
            )
            .all()
        )
        selected = select_best_matching_item(candidates, season)
        if selected is None:
            raise ValueError("Không tìm thấy món đồ phù hợp trong tủ đồ cho dịp/phong cách này")

        job.wardrobe_item_id = selected.id
        db.commit()

        garment_bytes = download_bytes_from_url(selected.blob_url)

        clothing_types = selected.attributes.get("clothing-type", [])
        selected_clothing_type = clothing_types[0] if clothing_types else None
        cloth_type = CLOTH_TYPE_BY_CLOTHING_TYPE.get(selected_clothing_type, "upper")

        ensure_container("results")

        front_person_bytes = download_bytes_from_url(front_image_url)
        front_result_bytes = call_catvton_service(front_person_bytes, garment_bytes, cloth_type)
        job.result_front_blob_url = upload_bytes("results", f"{job.user_id}/{job.id}-front.png", front_result_bytes)

        if side_image_url:
            side_person_bytes = download_bytes_from_url(side_image_url)
            side_result_bytes = call_catvton_service(side_person_bytes, garment_bytes, cloth_type)
            job.result_side_blob_url = upload_bytes("results", f"{job.user_id}/{job.id}-side.png", side_result_bytes)

        job.status = "done"
        db.commit()
    except Exception as error:  # noqa: BLE001 — any failure here must land the job in `failed`, not crash the background task
        job.status = "failed"
        job.error_message = str(error)
        db.commit()
