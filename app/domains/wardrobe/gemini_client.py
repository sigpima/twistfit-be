import base64
import json

import httpx

from app.core.config import settings
from app.domains.wardrobe.schemas import CATEGORIES, OCCASION_TAGS, STYLE_TAGS

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

PROMPT = (
    "Given this clothing image, classify it. Respond with ONLY a JSON "
    "object, no other text, in exactly this shape:\n"
    f'{{"category": "<one of {CATEGORIES}>", '
    f'"styleTags": [<subset of {STYLE_TAGS}>], '
    f'"occasionTags": [<subset of {OCCASION_TAGS}>]}}'
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
