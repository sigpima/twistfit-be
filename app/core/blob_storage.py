import time
from datetime import datetime, timedelta, timezone

import httpx
from azure.storage.blob import BlobSasPermissions, BlobServiceClient, ContentSettings, generate_blob_sas

from app.core.config import settings


def _client() -> BlobServiceClient:
    return BlobServiceClient.from_connection_string(settings.azure_storage_connection_string)


def ensure_container(container: str) -> None:
    # public_access="blob" allows anonymous reads of individual blobs (not
    # container listing) — fine here since wardrobe/result images aren't
    # sensitive; writes still require a signed SAS URL (see
    # generate_upload_sas_url).
    client = _client()
    container_client = client.get_container_client(container)
    if not container_client.exists():
        container_client.create_container(public_access="blob")


def blob_public_url(container: str, blob_path: str) -> str:
    return _client().get_blob_client(container=container, blob=blob_path).url


def generate_upload_sas_url(container: str, blob_path: str, expiry_minutes: int = 10) -> str:
    client = _client()
    sas_token = generate_blob_sas(
        account_name=client.account_name,
        container_name=container,
        blob_name=blob_path,
        account_key=client.credential.account_key,
        permission=BlobSasPermissions(write=True, create=True),
        expiry=datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes),
    )
    blob_client = client.get_blob_client(container=container, blob=blob_path)
    return f"{blob_client.url}?{sas_token}"


def upload_bytes(container: str, blob_path: str, data: bytes, content_type: str = "image/png") -> str:
    client = _client()
    blob_client = client.get_blob_client(container=container, blob=blob_path)
    blob_client.upload_blob(data, overwrite=True, content_settings=ContentSettings(content_type=content_type))
    return blob_client.url


def download_bytes(container: str, blob_path: str) -> bytes:
    client = _client()
    blob_client = client.get_blob_client(container=container, blob=blob_path)
    return blob_client.download_blob().readall()


_BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def download_bytes_from_url(url: str) -> bytes:
    # twistfit.org sits behind a WAF/CDN that resets connections from httpx's
    # default "python-httpx/..." User-Agent without sending a response
    # (surfaces as httpx.RemoteProtocolError). A browser-like UA passes.
    print(f"[TRYON-DEBUG] download_bytes_from_url start url={url}", flush=True)
    started = time.monotonic()
    try:
        response = httpx.get(url, timeout=30.0, headers={"User-Agent": _BROWSER_USER_AGENT})
    except Exception as error:
        elapsed = time.monotonic() - started
        print(
            f"[TRYON-DEBUG] download_bytes_from_url FAILED url={url} elapsed={elapsed:.3f}s "
            f"error_type={type(error).__name__} error={error!r}",
            flush=True,
        )
        raise
    elapsed = time.monotonic() - started
    print(
        f"[TRYON-DEBUG] download_bytes_from_url response url={url} elapsed={elapsed:.3f}s "
        f"status={response.status_code} content_length={len(response.content)}",
        flush=True,
    )
    response.raise_for_status()
    return response.content
