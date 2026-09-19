from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session

from app.core.blob_storage import download_bytes_from_url, ensure_container, upload_bytes
from app.core.config import settings
from app.domains.tryon.flux_vto_client import call_flux_vto, merge_garments_into_canvas
from app.domains.tryon.garment_selection import select_outfit_combo
from app.domains.tryon.models import TryOnJob, TryOnJobItem
from app.domains.wardrobe.models import WardrobeItem

_GARMENT_DESCRIPTION_BY_CATEGORY = {
    "ao": "shirt",
    "ao-khoac": "jacket",
    "quan": "pants",
    "vay": "skirt",
    "dam": "dress",
}


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


def _garment_description(item: WardrobeItem) -> str:
    clothing_types = item.attributes.get("clothing-type", [])
    category = clothing_types[0] if clothing_types else None
    return _GARMENT_DESCRIPTION_BY_CATEGORY.get(category, "garment")


def _build_vto_prompt(combo: list[WardrobeItem]) -> str:
    descriptions = [_garment_description(item) for item in combo]
    if len(descriptions) == 1:
        joined = descriptions[0]
    else:
        joined = ", ".join(descriptions[:-1]) + f" and {descriptions[-1]}"
    return (
        "The person of image 1, maintaining exactly their face and pose, "
        f"wearing the {joined} of image 2."
    )


def _apply_combo_via_flux_vto(person_bytes_list: list[bytes], combo: list[WardrobeItem]) -> list[bytes]:
    """Merge every combo item into one garment reference (FLUX VTO's
    documented approach for multi-garment try-on) and apply it to each
    angle (front/side) in one FLUX VTO call per angle."""
    garment_bytes_list = [download_bytes_from_url(item.blob_url) for item in combo]
    garment_reference = garment_bytes_list[0] if len(garment_bytes_list) == 1 else merge_garments_into_canvas(garment_bytes_list)
    prompt = _build_vto_prompt(combo)
    return [call_flux_vto(person_bytes, garment_reference, prompt=prompt) for person_bytes in person_bytes_list]


def process_job(db: Session, job_id: int, season: str, front_image_url: str, side_image_url: str | None = None) -> None:
    print(
        f"[TRYON-DEBUG] process_job start job_id={job_id} season={season} "
        f"front_image_url={front_image_url} side_image_url={side_image_url} "
        f"flux_api_base_url={settings.flux_api_base_url}",
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
            f"{[(item.id, _garment_description(item)) for item in combo]}",
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

        result_bytes_list = _apply_combo_via_flux_vto(person_bytes_list, combo)
        print(f"[TRYON-DEBUG] process_job job_id={job_id} _apply_combo_via_flux_vto done", flush=True)

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
