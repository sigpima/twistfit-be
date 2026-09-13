from sqlalchemy.orm import Session

from app.domains.auth import service

DEMO_USERS = [
    {"name": "Người dùng Test", "email": "user@twistfit.vn", "password": "user1234", "role": "user"},
    {"name": "Quản trị viên Test", "email": "admin@twistfit.vn", "password": "admin1234", "role": "admin"},
]


def seed_demo_users(db: Session) -> None:
    for demo in DEMO_USERS:
        if service.get_user_by_email(db, demo["email"]) is None:
            service.create_user(
                db, name=demo["name"], email=demo["email"], password=demo["password"], role=demo["role"]
            )
