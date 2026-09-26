import uuid

from app.core.blob_storage import (
    download_bytes,
    download_bytes_from_url,
    ensure_container,
    generate_upload_sas_url,
    upload_bytes,
)

CONTAINER = "test-container"


def test_upload_and_download_round_trip():
    ensure_container(CONTAINER)
    blob_path = f"{uuid.uuid4()}.png"

    url = upload_bytes(CONTAINER, blob_path, b"fake-image-bytes", content_type="image/png")

    assert download_bytes(CONTAINER, blob_path) == b"fake-image-bytes"
    assert blob_path in url


def test_download_bytes_from_url_fetches_over_http():
    ensure_container(CONTAINER)
    blob_path = f"{uuid.uuid4()}.png"
    url = upload_bytes(CONTAINER, blob_path, b"another-blob", content_type="image/png")

    result = download_bytes_from_url(url)

    assert result == b"another-blob"


def test_generate_upload_sas_url_contains_a_signature():
    ensure_container(CONTAINER)
    blob_path = f"{uuid.uuid4()}.png"

    url = generate_upload_sas_url(CONTAINER, blob_path)

    assert blob_path in url
    assert "X-Amz-Signature=" in url
