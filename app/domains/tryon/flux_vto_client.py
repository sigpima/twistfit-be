import base64
import io
import math
import time

import httpx
from PIL import Image

from app.core.config import settings

_TERMINAL_FAILURE_STATUSES = {"Error", "Failed", "Content Moderated", "Request Moderated", "Task not found"}
_POLL_INTERVAL_SECONDS = 1.0
_POLL_TIMEOUT_SECONDS = 60.0
_GRID_CELL_SIZE = 512


def merge_garments_into_canvas(garment_images: list[bytes]) -> bytes:
    """Arrange multiple garment reference images into a single grid canvas.

    Per BFL's FLUX VTO docs, a multi-garment try-on is done by merging all
    garment references into one canvas image and sending it as the single
    `garment` input — NOT by chaining one API call per garment. This reduces
    file-handling overhead and is what the model was tuned for.
    """
    if not garment_images:
        raise ValueError("At least one garment image is required")

    images = [Image.open(io.BytesIO(gb)).convert("RGB") for gb in garment_images]
    cols = math.ceil(math.sqrt(len(images)))
    rows = math.ceil(len(images) / cols)

    canvas = Image.new("RGB", (cols * _GRID_CELL_SIZE, rows * _GRID_CELL_SIZE), color="white")
    for index, image in enumerate(images):
        image.thumbnail((_GRID_CELL_SIZE, _GRID_CELL_SIZE))
        col, row = index % cols, index // cols
        cell_x, cell_y = col * _GRID_CELL_SIZE, row * _GRID_CELL_SIZE
        offset_x = cell_x + (_GRID_CELL_SIZE - image.width) // 2
        offset_y = cell_y + (_GRID_CELL_SIZE - image.height) // 2
        canvas.paste(image, (offset_x, offset_y))

    output = io.BytesIO()
    canvas.save(output, format="PNG")
    return output.getvalue()


def call_flux_vto(person_bytes: bytes, garment_bytes: bytes, prompt: str = "") -> bytes:
    """Apply garment(s) to a person image via BFL's FLUX VTO API.

    `garment_bytes` is a single reference image. For more than one garment,
    build it with `merge_garments_into_canvas()` first and describe every
    garment in `prompt` (BFL's recommended formula: "The person of image 1,
    maintaining exactly their face and pose, wearing the {garments} of
    image 2.").
    """
    url = f"{settings.flux_api_base_url}/v1/flux-tools/vto-v2"
    print(
        f"[TRYON-DEBUG] call_flux_vto start url={url} person_bytes={len(person_bytes)} "
        f"garment_bytes={len(garment_bytes)} prompt={prompt!r}",
        flush=True,
    )
    started = time.monotonic()
    try:
        submit_response = httpx.post(
            url,
            headers={"x-key": settings.flux_api_key},
            json={
                "prompt": prompt,
                "person": base64.b64encode(person_bytes).decode("ascii"),
                "garment": base64.b64encode(garment_bytes).decode("ascii"),
                "output_format": "png",
            },
            timeout=30.0,
        )
        if submit_response.status_code >= 400:
            # raise_for_status()'s own message doesn't include the response
            # body, which for a 422 is where BFL actually says which field
            # failed validation and why — print it before raising so that's
            # not lost.
            print(
                f"[TRYON-DEBUG] call_flux_vto submit error body: {submit_response.text}",
                flush=True,
            )
        submit_response.raise_for_status()
        polling_url = submit_response.json()["polling_url"]
        result_bytes = _poll_for_result(polling_url)
    except Exception as error:
        elapsed = time.monotonic() - started
        print(
            f"[TRYON-DEBUG] call_flux_vto FAILED url={url} elapsed={elapsed:.3f}s "
            f"error_type={type(error).__name__} error={error!r}",
            flush=True,
        )
        raise
    elapsed = time.monotonic() - started
    print(
        f"[TRYON-DEBUG] call_flux_vto response url={url} elapsed={elapsed:.3f}s content_length={len(result_bytes)}",
        flush=True,
    )
    return result_bytes


def _poll_for_result(polling_url: str) -> bytes:
    deadline = time.monotonic() + _POLL_TIMEOUT_SECONDS
    while True:
        poll_response = httpx.get(polling_url, headers={"x-key": settings.flux_api_key}, timeout=30.0)
        poll_response.raise_for_status()
        result = poll_response.json()
        status = result.get("status")

        if status == "Ready":
            image_url = result["result"]["sample"]
            image_response = httpx.get(image_url, timeout=30.0)
            image_response.raise_for_status()
            return image_response.content

        if status in _TERMINAL_FAILURE_STATUSES:
            raise RuntimeError(f"FLUX VTO request failed with status={status!r}: {result}")

        if time.monotonic() > deadline:
            raise TimeoutError(f"FLUX VTO polling timed out after {_POLL_TIMEOUT_SECONDS}s (last status={status!r})")

        time.sleep(_POLL_INTERVAL_SECONDS)
