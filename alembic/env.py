import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.db.session import Base
from app.domains.auth import models as auth_models  # noqa: F401
from app.domains.faq import models as faq_models  # noqa: F401
from app.domains.team import models as team_models  # noqa: F401
from app.domains.model_catalog import models as model_catalog_models  # noqa: F401
from app.domains.capsule_wardrobe import models as capsule_wardrobe_models  # noqa: F401
from app.domains.blog import models as blog_models  # noqa: F401

config = context.config
if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(url=settings.database_url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
