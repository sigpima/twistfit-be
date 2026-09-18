import base64

import httpx
import pytest

from app.core.config import settings
from app.domains.tryon.catvton_client import call_catvton_service, call_catvton_service_batch


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


def test_call_catvton_service_batch_sends_every_person_image_and_decodes_results(monkeypatch):
    captured = {}

    def fake_post(url, headers=None, files=None, data=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["files"] = files
        captured["data"] = data
        encoded = [base64.b64encode(b"front-result").decode("ascii"), base64.b64encode(b"side-result").decode("ascii")]
        return httpx.Response(200, json={"images": encoded}, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", fake_post)

    result = call_catvton_service_batch([b"front-bytes", b"side-bytes"], b"garment-bytes", "upper")

    assert result == [b"front-result", b"side-result"]
    assert captured["url"].endswith("/generate-batch")
    assert captured["headers"]["X-API-Key"] == settings.catvton_api_key
    assert captured["data"]["cloth_type"] == "upper"
    person_fields = [f for f in captured["files"] if f[0] == "person_images"]
    assert len(person_fields) == 2
    garment_fields = [f for f in captured["files"] if f[0] == "garment_image"]
    assert len(garment_fields) == 1


def test_call_catvton_service_batch_raises_on_error_status(monkeypatch):
    def fake_post(url, headers=None, files=None, data=None, timeout=None):
        return httpx.Response(500, content=b"error", request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(httpx.HTTPStatusError):
        call_catvton_service_batch([b"person-bytes"], b"garment-bytes", "upper")
