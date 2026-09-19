import base64
import json

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domains.accessories.schemas import ACCESSORY_CATEGORIES
from app.domains.quiz_attempts.schemas import PARENT_SEASONS
from app.domains.taxonomy import service as taxonomy_service

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent"


def _build_prompt(style_tags: list[str], occasion_tags: list[str]) -> str:
    return (
        "Given this fashion accessory product image, classify it. Respond with "
        "ONLY a JSON object, no other text, in exactly this shape:\n"
        f'{{"category": "<one of {ACCESSORY_CATEGORIES}>", '
        f'"styleTags": [<subset of {style_tags}>], '
        f'"occasionTags": [<subset of {occasion_tags}>], '
        f'"toneTags": [<subset of {PARENT_SEASONS}, the color season(s) this '
        'item suits best, or an empty list if it suits any season>]}}'
    )


def _call_gemini(image_bytes: bytes, prompt: str) -> str:
    response = httpx.post(
        GEMINI_URL,
        params={"key": settings.gemini_api_key},
        json={
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
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


def suggest_tags(image_bytes: bytes, db: Session) -> dict:
    style_tags = taxonomy_service.get_group_values(db, "style")
    occasion_tags = taxonomy_service.get_group_values(db, "occasion")
    prompt = _build_prompt(style_tags, occasion_tags)
    raw_text = _call_gemini(image_bytes, prompt)
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    return json.loads(cleaned)
