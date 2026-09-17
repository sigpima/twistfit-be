import json

from app.domains.accessories import gemini_client


def test_suggest_tags_parses_a_clean_json_response(monkeypatch):
    monkeypatch.setattr(
        gemini_client,
        "_call_gemini",
        lambda image_bytes: json.dumps(
            {
                "category": "tui-xach",
                "styleTags": ["casual"],
                "occasionTags": ["hang-ngay"],
                "toneTags": ["autumn"],
            }
        ),
    )

    result = gemini_client.suggest_tags(b"fake-bytes")

    assert result == {
        "category": "tui-xach",
        "styleTags": ["casual"],
        "occasionTags": ["hang-ngay"],
        "toneTags": ["autumn"],
    }


def test_suggest_tags_strips_markdown_code_fences(monkeypatch):
    monkeypatch.setattr(
        gemini_client,
        "_call_gemini",
        lambda image_bytes: (
            '```json\n{"category": "giay", "styleTags": ["formal"], '
            '"occasionTags": ["du-tiec"], "toneTags": []}\n```'
        ),
    )

    result = gemini_client.suggest_tags(b"fake-bytes")

    assert result["category"] == "giay"
    assert result["toneTags"] == []
