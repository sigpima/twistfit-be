from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import SessionLocal
from app.domains.auth.router import router as auth_router
from app.domains.auth.seed import seed_demo_users
from app.domains.faq.router import router as faq_router
from app.domains.faq.seed import seed_demo_faq_items
from app.domains.team.router import router as team_router
from app.domains.team.seed import seed_demo_team_members
from app.domains.model_catalog.router import router as model_catalog_router
from app.domains.model_catalog.seed import seed_demo_models

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        seed_demo_users(db)
        seed_demo_faq_items(db)
        seed_demo_team_members(db)
        seed_demo_models(db)
    finally:
        db.close()
    yield


app = FastAPI(title="TwistFit API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(faq_router)
app.include_router(team_router)
app.include_router(model_catalog_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
