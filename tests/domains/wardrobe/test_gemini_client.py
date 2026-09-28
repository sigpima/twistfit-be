import json

from google.genai import types

from app.core.config import settings
from app.domains.taxonomy.schemas import TaxonomyGroupInput, TaxonomyValueInput
from app.domains.taxonomy import service as taxonomy_service
from app.domains.wardrobe import gemini_client


class _FakeModels:
    def __init__(self, calls):
        self._calls = calls

    def generate_content(self, **kwargs):
        self._calls.append(kwargs)
        return type("Response", (), {"text": "fake-response-text"})()


class _FakeClient:
    def __init__(self, calls, **kwargs):
        self.init_kwargs = kwargs
        self.models = _FakeModels(calls)


def test_call_gemini_sends_the_prompt_and_image_and_returns_the_response_text(monkeypatch):
    calls = []
    monkeypatch.setattr(gemini_client.genai, "Client", lambda **kwargs: _FakeClient(calls, **kwargs))

    result = gemini_client._call_gemini(b"fake-image-bytes", "a test prompt")

    assert result == "fake-response-text"
    assert len(calls) == 1
    assert calls[0]["model"] == gemini_client.GEMINI_MODEL
    contents = calls[0]["contents"]
    assert contents[0] == "a test prompt"
    assert isinstance(contents[1], types.Part)
    assert contents[1].inline_data.data == b"fake-image-bytes"
    assert contents[1].inline_data.mime_type == "image/png"


def test_call_gemini_authenticates_with_the_configured_api_key_and_a_30s_timeout(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        gemini_client.genai, "Client", lambda **kwargs: captured.update(kwargs) or _FakeClient([], **kwargs)
    )

    gemini_client._call_gemini(b"fake-image-bytes", "a test prompt")

    assert captured["api_key"] == settings.gemini_api_key
    assert isinstance(captured["http_options"], types.HttpOptions)
    assert captured["http_options"].timeout == 20_000


def _seed_two_groups(db_session):
    clothing_type = taxonomy_service.create_group(db_session, TaxonomyGroupInput(key="clothing-type", label="Loại quần áo"))
    taxonomy_service.create_value(db_session, clothing_type.id, TaxonomyValueInput(key="ao", label="Áo"))
    taxonomy_service.create_value(db_session, clothing_type.id, TaxonomyValueInput(key="dam", label="Đầm"))

    style = taxonomy_service.create_group(db_session, TaxonomyGroupInput(key="style", label="Loại phong cách"))
    taxonomy_service.create_value(db_session, style.id, TaxonomyValueInput(key="casual", label="Casual"))


def test_suggest_tags_parses_a_clean_json_response_covering_every_group(monkeypatch, db_session):
    _seed_two_groups(db_session)
    monkeypatch.setattr(
        gemini_client,
        "_call_gemini",
        lambda image_bytes, prompt: json.dumps({"clothing-type": ["ao"], "style": ["casual"]}),
    )

    result = gemini_client.suggest_tags(b"fake-bytes", db_session)

    assert result == {"clothing-type": ["ao"], "style": ["casual"]}


def test_suggest_tags_strips_markdown_code_fences(monkeypatch, db_session):
    _seed_two_groups(db_session)
    monkeypatch.setattr(
        gemini_client,
        "_call_gemini",
        lambda image_bytes, prompt: '```json\n{"clothing-type": ["dam"], "style": []}\n```',
    )

    result = gemini_client.suggest_tags(b"fake-bytes", db_session)

    assert result["clothing-type"] == ["dam"]


def test_suggest_tags_drops_keys_that_are_not_real_groups(monkeypatch, db_session):
    _seed_two_groups(db_session)
    monkeypatch.setattr(
        gemini_client,
        "_call_gemini",
        lambda image_bytes, prompt: json.dumps({"clothing-type": ["ao"], "not-a-real-group": ["x"]}),
    )

    result = gemini_client.suggest_tags(b"fake-bytes", db_session)

    assert result == {"clothing-type": ["ao"]}


def test_suggest_tags_drops_values_that_are_not_real_values_in_their_group(monkeypatch, db_session):
    _seed_two_groups(db_session)
    monkeypatch.setattr(
        gemini_client,
        "_call_gemini",
        lambda image_bytes, prompt: json.dumps({"clothing-type": ["ao", "not-a-real-value"], "style": ["casual"]}),
    )

    result = gemini_client.suggest_tags(b"fake-bytes", db_session)

    assert result["clothing-type"] == ["ao"]


def test_build_prompt_lists_every_current_group_and_its_values(db_session):
    _seed_two_groups(db_session)
    groups = taxonomy_service.list_groups(db_session)

    prompt = gemini_client._build_prompt(groups)

    assert '"clothing-type"' in prompt
    assert "ao" in prompt and "dam" in prompt
    assert '"style"' in prompt
    assert "casual" in prompt
