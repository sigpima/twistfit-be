import base64

import httpx

from app.core.config import settings


def call_catvton_service(person_bytes: bytes, garment_bytes: bytes, cloth_type: str) -> bytes:
    response = httpx.post(
        f"{settings.catvton_service_url}/generate",
        headers={"X-API-Key": settings.catvton_api_key},
        files={
            "person_image": ("person.png", person_bytes, "image/png"),
            "garment_image": ("garment.png", garment_bytes, "image/png"),
        },
        data={"cloth_type": cloth_type},
        timeout=60.0,
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

    response = httpx.post(
        f"{settings.catvton_service_url}/generate-batch",
        headers={"X-API-Key": settings.catvton_api_key},
        files=files,
        data={"cloth_type": cloth_type},
        timeout=90.0,
    )
    response.raise_for_status()
    return [base64.b64decode(image) for image in response.json()["images"]]
