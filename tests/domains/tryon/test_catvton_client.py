import httpx
import pytest

from app.core.config import settings
from app.domains.tryon.catvton_client import call_catvton_service


def test_call_catvton_service_sends_the_api_key_and_returns_bytes(monkeypatch):
    captured = {}

    def fake_post(url, headers=None, files=None, data=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["data"] = data
        return httpx.Response(200, content=b"fake-result-bytes", request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", fake_post)

    result = call_catvton_service(b"person-bytes", b"garment-bytes", "upper")

    assert result == b"fake-result-bytes"
    assert captured["url"].endswith("/generate")
    assert captured["headers"]["X-API-Key"] == settings.catvton_api_key
    assert captured["data"]["cloth_type"] == "upper"


def test_call_catvton_service_raises_on_error_status(monkeypatch):
    def fake_post(url, headers=None, files=None, data=None, timeout=None):
        return httpx.Response(500, content=b"error", request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(httpx.HTTPStatusError):
        call_catvton_service(b"person-bytes", b"garment-bytes", "upper")
