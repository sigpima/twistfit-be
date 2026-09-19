import base64
import time

import httpx

from app.core.config import settings


def call_catvton_service(person_bytes: bytes, garment_bytes: bytes, cloth_type: str) -> bytes:
    url = f"{settings.catvton_service_url}/generate"
    print(
        f"[TRYON-DEBUG] call_catvton_service start url={url} "
        f"person_bytes={len(person_bytes)} garment_bytes={len(garment_bytes)} cloth_type={cloth_type}",
        flush=True,
    )
    started = time.monotonic()
    try:
        response = httpx.post(
            url,
            headers={"X-API-Key": settings.catvton_api_key},
            files={
                "person_image": ("person.png", person_bytes, "image/png"),
                "garment_image": ("garment.png", garment_bytes, "image/png"),
            },
            data={"cloth_type": cloth_type},
            timeout=60.0,
        )
    except Exception as error:
        elapsed = time.monotonic() - started
        print(
            f"[TRYON-DEBUG] call_catvton_service FAILED url={url} elapsed={elapsed:.3f}s "
            f"error_type={type(error).__name__} error={error!r}",
            flush=True,
        )
        raise
    elapsed = time.monotonic() - started
    print(
        f"[TRYON-DEBUG] call_catvton_service response url={url} elapsed={elapsed:.3f}s "
        f"status={response.status_code} content_length={len(response.content)}",
        flush=True,
    )
    response.raise_for_status()
    return response.content


def call_catvton_service_batch(
    person_bytes_list: list[bytes], garment_bytes: bytes, cloth_type: str
) -> list[bytes]:
    """Run every person image (e.g. a job's front and side angles) through
    the same garment/cloth_type in one request, so the service can batch
    them into a single GPU pass instead of one call per angle."""
    files = [("person_images", (f"person-{i}.png", pb, "image/png")) for i, pb in enumerate(person_bytes_list)]
    files.append(("garment_image", ("garment.png", garment_bytes, "image/png")))

    url = f"{settings.catvton_service_url}/generate-batch"
    total_person_bytes = sum(len(pb) for pb in person_bytes_list)
    print(
        f"[TRYON-DEBUG] call_catvton_service_batch start url={url} "
        f"person_images={len(person_bytes_list)} total_person_bytes={total_person_bytes} "
        f"garment_bytes={len(garment_bytes)} cloth_type={cloth_type}",
        flush=True,
    )
    started = time.monotonic()
    try:
        response = httpx.post(
            url,
            headers={"X-API-Key": settings.catvton_api_key},
            files=files,
            data={"cloth_type": cloth_type},
            timeout=180.0,
        )
    except Exception as error:
        elapsed = time.monotonic() - started
        print(
            f"[TRYON-DEBUG] call_catvton_service_batch FAILED url={url} elapsed={elapsed:.3f}s "
            f"error_type={type(error).__name__} error={error!r}",
            flush=True,
        )
        raise
    elapsed = time.monotonic() - started
    print(
        f"[TRYON-DEBUG] call_catvton_service_batch response url={url} elapsed={elapsed:.3f}s "
        f"status={response.status_code} content_length={len(response.content)}",
        flush=True,
    )
    response.raise_for_status()
    return [base64.b64decode(image) for image in response.json()["images"]]
