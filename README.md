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

## Local object storage (MinIO)

Wardrobe image uploads go through S3-compatible object storage via `boto3`.
`Settings.minio_endpoint`/`minio_public_endpoint` default to `http://localhost:9000`
with dev-only credentials, so no `.env` changes are needed for local dev —
just have MinIO listening there.

**With Docker** (`docker-compose.yml` already defines a `minio` service):

```bash
docker compose up -d minio
```

Console is at `http://localhost:9001` (root credentials from `docker-compose.yml`).

Buckets (e.g. `wardrobe`) are created on demand by the app itself
(`ensure_container` in `app/core/blob_storage.py`), which also sets the
public-read policy and CORS rule needed for the frontend to `PUT` directly
to a presigned URL from the browser — nothing to pre-create or configure
by hand.

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
