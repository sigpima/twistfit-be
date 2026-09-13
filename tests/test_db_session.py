from sqlalchemy import text

from app.db.session import SessionLocal


def test_can_connect_and_query():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT 1")).scalar_one()
        assert result == 1
    finally:
        db.close()
