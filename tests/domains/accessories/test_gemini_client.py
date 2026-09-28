import json

from google.genai import types

from app.core.config import settings
from app.domains.accessories import gemini_client


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
    assert captured["http_options"].timeout == 30_000


def test_suggest_tags_parses_a_clean_json_response(monkeypatch, db_session):
    monkeypatch.setattr(
        gemini_client,
        "_call_gemini",
        lambda image_bytes, prompt: json.dumps(
            {
                "category": "tui-xach",
                "styleTags": ["casual"],
                "occasionTags": ["hang-ngay"],
                "toneTags": ["autumn"],
            }
        ),
    )

    result = gemini_client.suggest_tags(b"fake-bytes", db_session)

    assert result == {
        "category": "tui-xach",
        "styleTags": ["casual"],
        "occasionTags": ["hang-ngay"],
        "toneTags": ["autumn"],
    }


def test_suggest_tags_strips_markdown_code_fences(monkeypatch, db_session):
    monkeypatch.setattr(
        gemini_client,
        "_call_gemini",
        lambda image_bytes, prompt: (
            '```json\n{"category": "giay", "styleTags": ["formal"], '
            '"occasionTags": ["du-tiec"], "toneTags": []}\n```'
        ),
    )

    result = gemini_client.suggest_tags(b"fake-bytes", db_session)

    assert result["category"] == "giay"
    assert result["toneTags"] == []
