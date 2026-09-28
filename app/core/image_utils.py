import io

import pillow_avif  # noqa: F401 — import side effect registers AVIF codec support with Pillow
from PIL import Image


def normalize_to_png(image_bytes: bytes) -> bytes:
    # Browser uploads can be any format the browser happens to produce
    # (avif, webp, heic...) while blob storage paths and the Gemini
    # inline_data mime_type are both hardcoded to image/png — convert once
    # here, right after downloading, so every caller downstream can safely
    # assume real PNG bytes regardless of what the user actually uploaded.
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
