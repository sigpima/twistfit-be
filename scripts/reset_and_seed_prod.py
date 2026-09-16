"""One-off ops script: wipe a Postgres database, run migrations from scratch,
then seed all demo content (users, FAQ, team, model catalog, capsule
wardrobe, blog, quiz questions).

DESTRUCTIVE. Drops every table in the target database's public schema.
Intended for the production database before it has any real user data.

Usage:
    cd backend && source venv/bin/activate
    DATABASE_URL="postgresql+psycopg://user:password@host:5432/dbname?sslmode=require" \\
        python3 scripts/reset_and_seed_prod.py

The script requires the DATABASE_URL env var (does not read backend/.env,
so it can never silently target your local dev database) and asks for a
typed confirmation before touching anything.
"""

import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

BACKEND_DIR = Path(__file__).resolve().parents[1]


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: set the DATABASE_URL env var to the target database before running this.")
        sys.exit(1)

    host = urlsplit(database_url.replace("postgresql+psycopg", "postgresql")).hostname or "?"
    if host in ("localhost", "127.0.0.1"):
        print(f"ERROR: DATABASE_URL points at {host} - this script is for the production database only.")
        sys.exit(1)

    print("This will PERMANENTLY DELETE every table in this database and rebuild it from scratch:")
    print(f"  host: {host}")
    print(f"  url:  {database_url.split('@')[-1]}")
    print()
    typed = input("Type RESET PRODUCTION to continue: ")
    if typed != "RESET PRODUCTION":
        print("Aborted - confirmation text did not match.")
        sys.exit(1)

    # Import only after confirmation, and only after DATABASE_URL is confirmed set,
    # since app.db.session builds its engine from settings.database_url at import time.
    from sqlalchemy import create_engine, text

    print("\n[1/3] Dropping and recreating the public schema...")
    engine = create_engine(database_url)
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()
    engine.dispose()

    print("[2/3] Running alembic migrations (upgrade head)...")
    subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=BACKEND_DIR,
        env={**os.environ, "DATABASE_URL": database_url},
        check=True,
    )

    print("[3/3] Seeding demo content (users, FAQ, team, model catalog, capsule wardrobe, blog, quiz)...")
    from app.db.session import SessionLocal
    from app.domains.auth.seed import seed_demo_users
    from app.domains.faq.seed import seed_demo_faq_items
    from app.domains.team.seed import seed_demo_team_members
    from app.domains.model_catalog.seed import seed_demo_models
    from app.domains.capsule_wardrobe.seed import seed_demo_capsule_sets
    from app.domains.blog.seed import seed_demo_blog_posts
    from app.domains.quiz.seed import seed_demo_quiz_questions

    db = SessionLocal()
    try:
        seed_demo_users(db)
        seed_demo_faq_items(db)
        seed_demo_team_members(db)
        seed_demo_models(db)
        seed_demo_capsule_sets(db)
        seed_demo_blog_posts(db)
        seed_demo_quiz_questions(db)
    finally:
        db.close()

    print("\nDone. Database reset and reseeded.")
    print("Reminder: seed_demo_users creates a demo admin account with a hardcoded password")
    print("(see app/domains/auth/seed.py) - change it before exposing this environment publicly.")


if __name__ == "__main__":
    main()
