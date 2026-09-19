import base64
import io

import httpx
import pytest
from PIL import Image

from app.core.config import settings
from app.domains.tryon.flux_vto_client import call_flux_vto, merge_garments_into_canvas


def _fake_image_bytes(color: tuple[int, int, int], size: tuple[int, int] = (100, 200)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format="PNG")
    return buffer.getvalue()


def test_merge_garments_into_canvas_arranges_images_in_a_grid():
    garments = [_fake_image_bytes((255, 0, 0)), _fake_image_bytes((0, 255, 0)), _fake_image_bytes((0, 0, 255))]

    result = merge_garments_into_canvas(garments)

    canvas = Image.open(io.BytesIO(result))
    # 3 images -> ceil(sqrt(3))=2 columns, ceil(3/2)=2 rows, 512px cells
    assert canvas.size == (1024, 1024)


def test_merge_garments_into_canvas_single_garment_still_works():
    result = merge_garments_into_canvas([_fake_image_bytes((255, 0, 0))])

    canvas = Image.open(io.BytesIO(result))
    assert canvas.size == (512, 512)


def test_merge_garments_into_canvas_rejects_empty_list():
    with pytest.raises(ValueError):
        merge_garments_into_canvas([])


def test_call_flux_vto_submits_then_polls_and_returns_image_bytes(monkeypatch):
    calls = {"post": [], "get": []}
    monkeypatch.setattr(
        "app.domains.tryon.flux_vto_client._POLL_INTERVAL_SECONDS", 0
    )

    def fake_post(url, headers=None, json=None, timeout=None):
        calls["post"].append({"url": url, "headers": headers, "json": json})
        return httpx.Response(
            200,
            json={"id": "job-123", "polling_url": "https://api.bfl.ai/v1/get_result?id=job-123"},
            request=httpx.Request("POST", url),
        )

    poll_responses = iter(
        [
            httpx.Response(200, json={"id": "job-123", "status": "Pending"}, request=httpx.Request("GET", "x")),
            httpx.Response(
                200,
                json={"id": "job-123", "status": "Ready", "result": {"sample": "https://delivery.bfl.ai/result.png"}},
                request=httpx.Request("GET", "x"),
            ),
        ]
    )

    def fake_get(url, headers=None, timeout=None):
        calls["get"].append({"url": url, "headers": headers})
        if url == "https://delivery.bfl.ai/result.png":
            return httpx.Response(200, content=b"result-image-bytes", request=httpx.Request("GET", url))
        return next(poll_responses)

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(httpx, "get", fake_get)

    result = call_flux_vto(b"person-bytes", b"garment-bytes", prompt="add a red jacket")

    assert result == b"result-image-bytes"
    assert calls["post"][0]["url"].endswith("/v1/flux-tools/vto-v2")
    assert calls["post"][0]["headers"]["x-key"] == settings.flux_api_key
    assert calls["post"][0]["json"]["prompt"] == "add a red jacket"
    assert calls["post"][0]["json"]["person"] == base64.b64encode(b"person-bytes").decode("ascii")
    assert calls["post"][0]["json"]["garment"] == base64.b64encode(b"garment-bytes").decode("ascii")
    # polled twice (Pending, then Ready) before fetching the delivered image
    assert len(calls["get"]) == 3


def test_call_flux_vto_raises_on_submit_error_status(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return httpx.Response(400, content=b"bad request", request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(httpx.HTTPStatusError):
        call_flux_vto(b"person-bytes", b"garment-bytes")


def test_call_flux_vto_raises_runtime_error_on_terminal_failure_status(monkeypatch):
    def fake_post(url, headers=None, json=None, timeout=None):
        return httpx.Response(
            200,
            json={"id": "job-123", "polling_url": "https://api.bfl.ai/v1/get_result?id=job-123"},
            request=httpx.Request("POST", url),
        )

    def fake_get(url, headers=None, timeout=None):
        return httpx.Response(
            200,
            json={"id": "job-123", "status": "Content Moderated"},
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(httpx, "get", fake_get)

    with pytest.raises(RuntimeError, match="Content Moderated"):
        call_flux_vto(b"person-bytes", b"garment-bytes")


def test_call_flux_vto_raises_timeout_error_if_never_ready(monkeypatch):
    monkeypatch.setattr("app.domains.tryon.flux_vto_client._POLL_INTERVAL_SECONDS", 0)
    monkeypatch.setattr("app.domains.tryon.flux_vto_client._POLL_TIMEOUT_SECONDS", 0)

    def fake_post(url, headers=None, json=None, timeout=None):
        return httpx.Response(
            200,
            json={"id": "job-123", "polling_url": "https://api.bfl.ai/v1/get_result?id=job-123"},
            request=httpx.Request("POST", url),
        )

    def fake_get(url, headers=None, timeout=None):
        return httpx.Response(200, json={"id": "job-123", "status": "Pending"}, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(httpx, "get", fake_get)

    with pytest.raises(TimeoutError):
        call_flux_vto(b"person-bytes", b"garment-bytes")
