from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session

from app.core.blob_storage import download_bytes_from_url, ensure_container, upload_bytes
from app.core.config import settings
from app.domains.tryon.catvton_client import call_catvton_service_batch
from app.domains.tryon.garment_selection import CLOTH_TYPE_BY_CATEGORY, select_outfit_combo
from app.domains.tryon.models import TryOnJob, TryOnJobItem
from app.domains.wardrobe.models import WardrobeItem


def create_job(
    db: Session, user_id: int, catalog_model_id: int, occasion: str | None, style: str | None
) -> TryOnJob:
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


def list_jobs(db: Session, user_id: int) -> list[TryOnJob]:
    return db.query(TryOnJob).filter(TryOnJob.user_id == user_id).order_by(TryOnJob.created_at.desc()).all()


def _cloth_type_of(item: WardrobeItem) -> str:
    clothing_types = item.attributes.get("clothing-type", [])
    category = clothing_types[0] if clothing_types else None
    return CLOTH_TYPE_BY_CATEGORY.get(category, "upper")


def _apply_combo_batch(person_bytes_list: list[bytes], combo: list[WardrobeItem]) -> list[bytes]:
    """Apply every combo item to every angle, one combo step at a time —
    each step batches all angles (e.g. front+side) into a single call."""
    current_bytes_list = person_bytes_list
    for item in combo:
        garment_bytes = download_bytes_from_url(item.blob_url)
        current_bytes_list = call_catvton_service_batch(current_bytes_list, garment_bytes, _cloth_type_of(item))
    return current_bytes_list


def process_job(db: Session, job_id: int, season: str, front_image_url: str, side_image_url: str | None = None) -> None:
    print(
        f"[TRYON-DEBUG] process_job start job_id={job_id} season={season} "
        f"front_image_url={front_image_url} side_image_url={side_image_url} "
        f"catvton_service_url={settings.catvton_service_url}",
        flush=True,
    )
    job = db.get(TryOnJob, job_id)
    if job is None:
        print(f"[TRYON-DEBUG] process_job job_id={job_id} not found in DB, aborting", flush=True)
        return

    job.status = "processing"
    db.commit()

    try:
        tag_attribute = "occasion" if job.occasion is not None else "style"
        tag_value = job.occasion if job.occasion is not None else job.style
        candidates = (
            db.query(WardrobeItem)
            .filter(
                WardrobeItem.user_id == job.user_id,
                cast(WardrobeItem.attributes[tag_attribute], JSONB).contains([tag_value]),
            )
            .all()
        )
        if not candidates:
            raise ValueError("Không tìm thấy món đồ phù hợp trong tủ đồ cho dịp/phong cách này")

        combo = select_outfit_combo(candidates, season)
        if combo is None:
            raise ValueError("Tủ đồ chưa đủ trang phục để ghép thành 1 bộ hoàn chỉnh cho dịp/phong cách này")

        job.wardrobe_item_id = combo[0].id
        for index, item in enumerate(combo):
            db.add(TryOnJobItem(tryon_job_id=job.id, wardrobe_item_id=item.id, sort_order=index))
        db.commit()
        print(
            f"[TRYON-DEBUG] process_job job_id={job_id} combo selected: "
            f"{[(item.id, _cloth_type_of(item)) for item in combo]}",
            flush=True,
        )

        ensure_container("results")

        person_bytes_list = [download_bytes_from_url(front_image_url)]
        if side_image_url:
            person_bytes_list.append(download_bytes_from_url(side_image_url))
        print(
            f"[TRYON-DEBUG] process_job job_id={job_id} downloaded person images: "
            f"{[len(b) for b in person_bytes_list]} bytes",
            flush=True,
        )

        result_bytes_list = _apply_combo_batch(person_bytes_list, combo)
        print(f"[TRYON-DEBUG] process_job job_id={job_id} _apply_combo_batch done", flush=True)

        job.result_front_blob_url = upload_bytes("results", f"{job.user_id}/{job.id}-front.png", result_bytes_list[0])
        if side_image_url:
            job.result_side_blob_url = upload_bytes(
                "results", f"{job.user_id}/{job.id}-side.png", result_bytes_list[1]
            )

        job.status = "done"
        db.commit()
        print(f"[TRYON-DEBUG] process_job job_id={job_id} DONE", flush=True)
    except Exception as error:  # noqa: BLE001 — any failure here must land the job in `failed`, not crash the background task
        print(
            f"[TRYON-DEBUG] process_job job_id={job_id} EXCEPTION error_type={type(error).__name__} error={error!r}",
            flush=True,
        )
        job.status = "failed"
        job.error_message = str(error)
        db.commit()
