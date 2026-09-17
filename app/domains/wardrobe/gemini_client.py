import base64
import json

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domains.taxonomy import service as taxonomy_service
from app.domains.taxonomy.models import TaxonomyGroup

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"


def _build_prompt(groups: list[TaxonomyGroup]) -> str:
    field_descriptions = ", ".join(
        f'"{group.key}": [<subset of {[value.key for value in group.values]}>]' for group in groups
    )
    return (
        "Given this clothing image, classify it using EVERY one of the following attribute "
        "groups. Respond with ONLY a JSON object, no other text, in exactly this shape:\n"
        f"{{{field_descriptions}}}"
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


def _filter_valid(parsed: dict, groups: list[TaxonomyGroup]) -> dict[str, list[str]]:
    valid_values_by_group = {group.key: {value.key for value in group.values} for group in groups}
    result: dict[str, list[str]] = {}
    for key, values in parsed.items():
        if key not in valid_values_by_group or not isinstance(values, list):
            continue
        result[key] = [value for value in values if value in valid_values_by_group[key]]
    return result


def suggest_tags(image_bytes: bytes, db: Session) -> dict[str, list[str]]:
    groups = taxonomy_service.list_groups(db)
    prompt = _build_prompt(groups)
    raw_text = _call_gemini(image_bytes, prompt)
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()
    parsed = json.loads(cleaned)
    return _filter_valid(parsed, groups)
