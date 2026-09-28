from datetime import date, datetime, timedelta, timezone

from sqlalchemy import cast, func, update
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.core.blob_storage import download_bytes_from_url, ensure_container, upload_bytes
from app.core.config import settings
from app.domains.tryon.flux_vto_client import call_flux_vto, merge_garments_into_canvas
from app.domains.tryon.garment_selection import select_outfit_combo
from app.domains.tryon.models import TryOnDailyQuota, TryOnJob, TryOnJobItem
from app.domains.wardrobe.models import WardrobeItem

_GARMENT_DESCRIPTION_BY_CATEGORY = {
    "ao": "shirt",
    "ao-khoac": "jacket",
    "quan": "pants",
    "vay": "skirt",
    "dam": "dress",
}

DAILY_TRYON_LIMIT = 5
_VN_OFFSET = timedelta(hours=7)


def _vn_today() -> date:
    return (datetime.now(timezone.utc) + _VN_OFFSET).date()


def reserve_tryon_quota(db: Session, user_id: int, limit: int = DAILY_TRYON_LIMIT) -> bool:
    """Atomically reserve 1 of today's `limit` FLUX-VTO-billed attempts for
    this user. Race-safe under concurrent requests: Postgres resolves the
    ON CONFLICT branch under a row lock, so two simultaneous callers can
    never both push `used_count` past `limit`. Returns False (no row
    changed) once the limit is already reached.
    """
    quota_date = _vn_today()
    stmt = (
        pg_insert(TryOnDailyQuota)
        .values(user_id=user_id, quota_date=quota_date, used_count=1)
        .on_conflict_do_update(
            index_elements=["user_id", "quota_date"],
            set_={"used_count": TryOnDailyQuota.used_count + 1},
            where=TryOnDailyQuota.used_count < limit,
        )
        .returning(TryOnDailyQuota.used_count)
    )
    reserved = db.execute(stmt).first() is not None
    db.commit()
    return reserved


def release_tryon_quota(db: Session, user_id: int) -> None:
    """Refund 1 reserved attempt — call only when a job fails before it
    actually reached the paid FLUX VTO call."""
    quota_date = _vn_today()
    db.execute(
        update(TryOnDailyQuota)
        .where(
            TryOnDailyQuota.user_id == user_id,
            TryOnDailyQuota.quota_date == quota_date,
            TryOnDailyQuota.used_count > 0,
        )
        .values(used_count=TryOnDailyQuota.used_count - 1)
    )
    db.commit()


def get_tryon_quota(db: Session, user_id: int, limit: int = DAILY_TRYON_LIMIT) -> tuple[int, int]:
    """Returns (used_today, remaining_today) for the caller's Vietnam-calendar day."""
    quota_date = _vn_today()
    row = (
        db.query(TryOnDailyQuota)
        .filter(TryOnDailyQuota.user_id == user_id, TryOnDailyQuota.quota_date == quota_date)
        .first()
    )
    used = row.used_count if row else 0
    return used, max(limit - used, 0)


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


def delete_job(db: Session, user_id: int, job_id: int) -> bool:
    job = get_job(db, user_id, job_id)
    if job is None:
        return False
    db.delete(job)
    db.commit()
    return True


def _usage_counts(db: Session, user_id: int) -> dict[int, int]:
    """How many of the user's own successful ("done") combos each wardrobe
    item has appeared in — fed into select_outfit_combo so repeat combos
    don't keep reusing the same few pieces. Only "done" jobs count: a job
    that failed after item selection but before FLUX VTO succeeded (e.g.
    the API-key/network issues already hit in prod) would otherwise unfairly
    penalize items the user never actually saw a result for.
    """
    rows = (
        db.query(TryOnJobItem.wardrobe_item_id, func.count(TryOnJobItem.id))
        .join(TryOnJob, TryOnJob.id == TryOnJobItem.tryon_job_id)
        .filter(TryOnJob.user_id == user_id, TryOnJob.status == "done")
        .group_by(TryOnJobItem.wardrobe_item_id)
        .all()
    )
    return dict(rows)


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


def _build_garment_reference(combo: list[WardrobeItem]) -> bytes:
    """Download and, for a multi-item combo, merge every combo item into one
    garment reference image (FLUX VTO's documented approach for multi-garment
    try-on). Free — no paid FLUX VTO call happens here."""
    garment_bytes_list = [download_bytes_from_url(item.blob_url) for item in combo]
    return garment_bytes_list[0] if len(garment_bytes_list) == 1 else merge_garments_into_canvas(garment_bytes_list)


def _apply_combo_via_flux_vto(
    person_bytes_list: list[bytes], combo: list[WardrobeItem], garment_reference: bytes
) -> list[bytes]:
    """Apply the garment reference to each angle (front/side) in one paid
    FLUX VTO call per angle."""
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

    reached_flux = False
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

        usage_counts = _usage_counts(db, job.user_id)
        combo = select_outfit_combo(candidates, season, usage_counts)
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

        garment_reference = _build_garment_reference(combo)

        reached_flux = True
        result_bytes_list = _apply_combo_via_flux_vto(person_bytes_list, combo, garment_reference)
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
        if not reached_flux:
            # Failed before the paid FLUX VTO call was ever attempted (e.g. no
            # matching wardrobe items) — refund the reserved daily attempt.
            release_tryon_quota(db, job.user_id)
