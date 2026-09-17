import base64
import json

import httpx

from app.core.config import settings
from app.domains.accessories.schemas import ACCESSORY_CATEGORIES
from app.domains.quiz_attempts.schemas import PARENT_SEASONS
from app.domains.wardrobe.schemas import OCCASION_TAGS, STYLE_TAGS

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"

PROMPT = (
    "Given this fashion accessory product image, classify it. Respond with "
    "ONLY a JSON object, no other text, in exactly this shape:\n"
    f'{{"category": "<one of {ACCESSORY_CATEGORIES}>", '
    f'"styleTags": [<subset of {STYLE_TAGS}>], '
    f'"occasionTags": [<subset of {OCCASION_TAGS}>], '
    f'"toneTags": [<subset of {PARENT_SEASONS}, the color season(s) this '
    'item suits best, or an empty list if it suits any season>]}}'
)


def _call_gemini(image_bytes: bytes) -> str:
    response = httpx.post(
        GEMINI_URL,
        params={"key": settings.gemini_api_key},
        json={
            "contents": [
                {
                    "parts": [
                        {"text": PROMPT},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": base64.b64encode(image_bytes).decode(),
                            }
                        },
                    ]
                }
            ]
        },
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]


def suggest_tags(image_bytes: bytes) -> dict:
    raw_text = _call_gemini(image_bytes)
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    return json.loads(cleaned)
