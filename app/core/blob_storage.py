import json
import time

import boto3
import httpx
from botocore.client import Config
from botocore.exceptions import ClientError

from app.core.config import settings

ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
}


def _client(endpoint: str):
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def _internal_client():
    return _client(settings.minio_endpoint)


def _public_client():
    return _client(settings.minio_public_endpoint)


def _public_read_policy(bucket: str) -> str:
    # Anonymous read of individual objects, no bucket listing — mirrors the
    # Azure public_access="blob" container ACL this replaces.
    return json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket}/*"],
                }
            ],
        }
    )


def _cors_configuration() -> dict:
    # Lets the browser PUT directly to a presigned URL on this bucket from
    # any origin — a valid signature is still required to write, so this
    # only relaxes the browser-side check, not the actual authorization.
    return {
        "CORSRules": [
            {
                "AllowedOrigins": ["*"],
                "AllowedMethods": ["GET", "PUT", "HEAD"],
                "AllowedHeaders": ["*"],
                "ExposeHeaders": ["ETag"],
                "MaxAgeSeconds": 3600,
            }
        ]
    }


def ensure_container(container: str) -> None:
    client = _internal_client()
    try:
        client.head_bucket(Bucket=container)
    except ClientError:
        client.create_bucket(Bucket=container)
        client.put_bucket_policy(Bucket=container, Policy=_public_read_policy(container))
        client.put_bucket_cors(Bucket=container, CORSConfiguration=_cors_configuration())


def blob_public_url(container: str, blob_path: str) -> str:
    return f"{settings.minio_public_endpoint.rstrip('/')}/{container}/{blob_path}"


def generate_upload_sas_url(container: str, blob_path: str, expiry_minutes: int = 10) -> str:
    # Signed against the public endpoint rather than the internal one: SigV4
    # signs the Host header, so the URL must already carry the host the
    # browser will actually send the PUT to (see settings.minio_public_endpoint).
    client = _public_client()
    return client.generate_presigned_url(
        "put_object",
        Params={"Bucket": container, "Key": blob_path},
        ExpiresIn=expiry_minutes * 60,
    )


def upload_bytes(container: str, blob_path: str, data: bytes, content_type: str = "image/png") -> str:
    client = _internal_client()
    client.put_object(Bucket=container, Key=blob_path, Body=data, ContentType=content_type)
    return blob_public_url(container, blob_path)


def download_bytes(container: str, blob_path: str) -> bytes:
    client = _internal_client()
    response = client.get_object(Bucket=container, Key=blob_path)
    return response["Body"].read()


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
