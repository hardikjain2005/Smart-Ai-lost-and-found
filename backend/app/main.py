from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app import models  # noqa: F401  (register tables)
from app.api import admin, auth, claims, health, items, uploads
from app.core.config import get_settings
from app.core.errors import register_exception_handlers
from app.db.migrations import apply_additive_migrations
from app.db.session import Base, SessionLocal, engine
from app.services.seed import seed_demo_data

settings = get_settings()
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # MVP: create tables directly. Replace with Alembic migrations before production.
    Base.metadata.create_all(engine)
    apply_additive_migrations(engine)
    with SessionLocal() as db:
        seed_demo_data(db)
    yield


app = FastAPI(title=settings.app_name, version="0.2.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)
for r in (health.router, auth.router, items.router, claims.router, admin.router, uploads.router):
    app.include_router(r, prefix="/api")
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
