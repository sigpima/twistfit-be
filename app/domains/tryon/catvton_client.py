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
