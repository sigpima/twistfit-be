# TwistFit Backend (FastAPI)

## Local setup

1. Install PostgreSQL and create `twistfit_dev` / `twistfit_test` databases (see
   `docs/superpowers/plans/2026-09-13-fastapi-backend-foundation.md`, Task 1,
   in the frontend repo for exact commands).
2. `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and adjust values for local dev (in particular
   set `COOKIE_SECURE=false` and leave `COOKIE_DOMAIN` unset for `localhost`).
4. `alembic upgrade head`
5. Start local object storage (see below) — required for the wardrobe upload flow.
6. `uvicorn app.main:app --reload`

## Local object storage (Azurite)

Wardrobe image uploads go through Azure Blob Storage. `Settings.azure_storage_connection_string`
defaults to Azurite's well-known local credentials, so no `.env` changes are
needed for local dev — just have something listening on `127.0.0.1:10000`.

**With Docker** (`docker-compose.yml` already defines an `azurite` service):

```bash
docker compose up -d azurite
```

**Without Docker**, run Azurite directly via `npx`, with its data persisted
under the gitignored `.azurite/` directory in this repo:

```bash
nohup npx --yes azurite --silent --location .azurite --blobHost 127.0.0.1 > .azurite/azurite.log 2>&1 &
```

Either way, Azurite needs a CORS rule before the frontend can `PUT` directly
to a SAS-signed blob URL from the browser (Azurite doesn't ship one by
default). Run once per fresh `.azurite/` data directory:

```bash
python3 - <<'EOF'
from azure.storage.blob import BlobServiceClient, CorsRule

client = BlobServiceClient.from_connection_string(
    "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)
client.set_service_properties(cors=[CorsRule(
    allowed_origins=["*"],
    allowed_methods=["GET", "PUT", "POST", "HEAD", "OPTIONS"],
    allowed_headers=["*"],
    exposed_headers=["*"],
    max_age_in_seconds=3600,
)])
EOF
```

Containers (e.g. `wardrobe`) are created on demand by the app itself
(`ensure_container` in `app/core/blob_storage.py`) — nothing to pre-create.

## Adding a new domain

Each domain under `app/domains/<name>/` is self-contained:

- `models.py` — SQLAlchemy models, subclassing `app.db.session.Base`.
- `schemas.py` — Pydantic request/response schemas. Extend
  `app.domains.auth.schemas.CamelModel` so JSON keys are camelCase, matching
  the frontend's existing TypeScript types.
- `service.py` — business logic, taking a `Session` as an explicit parameter.
- `router.py` — FastAPI routes, mounted in `app/main.py` via
  `app.include_router(...)`.

Tests mirror the same shape under `tests/domains/<name>/`, using the
`db_session` and `client` fixtures from `tests/conftest.py` (no mocks, no
SQLite — always the real Postgres test database).

To add tables for a new domain: add
`from app.domains.<name> import models as <name>_models  # noqa: F401` to
`alembic/env.py`, then run `alembic revision --autogenerate -m "..."` and
`alembic upgrade head`.

Protect an authenticated route with `Depends(app.deps.get_current_user)`;
protect an admin-only route with `Depends(app.deps.require_admin)`.
