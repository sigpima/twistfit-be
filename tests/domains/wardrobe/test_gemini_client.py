import json

from app.domains.wardrobe import gemini_client


def test_suggest_tags_parses_a_clean_json_response(monkeypatch):
    monkeypatch.setattr(
        gemini_client,
        "_call_gemini",
        lambda image_bytes: json.dumps(
            {"category": "ao-thun", "styleTags": ["casual"], "occasionTags": ["hang-ngay"]}
        ),
    )

    result = gemini_client.suggest_tags(b"fake-bytes")

    assert result == {"category": "ao-thun", "styleTags": ["casual"], "occasionTags": ["hang-ngay"]}


def test_suggest_tags_strips_markdown_code_fences(monkeypatch):
    monkeypatch.setattr(
        gemini_client,
        "_call_gemini",
        lambda image_bytes: '```json\n{"category": "dam", "styleTags": ["formal"], "occasionTags": ["du-tiec"]}\n```',
    )

    result = gemini_client.suggest_tags(b"fake-bytes")

    assert result["category"] == "dam"
    assert result["styleTags"] == ["formal"]
