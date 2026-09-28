import json

from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from app.core.config import settings
from app.domains.accessories.schemas import ACCESSORY_CATEGORIES
from app.domains.quiz_attempts.schemas import PARENT_SEASONS
from app.domains.taxonomy import service as taxonomy_service

GEMINI_MODEL = "gemini-3.5-flash-lite"


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
    client = genai.Client(api_key=settings.gemini_api_key, http_options=types.HttpOptions(timeout=30_000))
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[prompt, types.Part.from_bytes(data=image_bytes, mime_type="image/png")],
        # No tools/function calling here, so automatic function calling has
        # nothing to do — disabling it silences the SDK's unconditional
        # "use Chat.send_message instead" warning on every call.
        config=types.GenerateContentConfig(
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        ),
    )
    return response.text


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
