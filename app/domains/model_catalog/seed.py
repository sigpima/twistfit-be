from sqlalchemy.orm import Session

from app.domains.model_catalog.models import CatalogModel

DEMO_MODELS = [
    {
        "name": "Mảnh mai", "image": "/outfit/models/female-1.jpg", "side_image": "/outfit/models/female-1-side.jpg",
        "dossier_image": "/outfit/models/female-1.jpg", "pose_count": 2, "tagline": "Mảnh mai",
        "undertone": "neutral", "height": "—", "body_shape": "—", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Thể thao", "image": "/outfit/models/female-2.jpg", "side_image": "/outfit/models/female-2-side.jpg",
        "dossier_image": "/outfit/models/female-2.jpg", "pose_count": 2, "tagline": "Thể thao",
        "undertone": "neutral", "height": "—", "body_shape": "—", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Nhỏ nhắn", "image": "/outfit/models/female-3.jpg", "side_image": "/outfit/models/female-3-side.jpg",
        "dossier_image": "/outfit/models/female-3.jpg", "pose_count": 2, "tagline": "Nhỏ nhắn",
        "undertone": "neutral", "height": "—", "body_shape": "—", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Cân đối", "image": "/outfit/models/female-4.jpg", "side_image": "/outfit/models/female-4-side.jpg",
        "dossier_image": "/outfit/models/female-4.jpg", "pose_count": 2, "tagline": "Cân đối",
        "undertone": "neutral", "height": "—", "body_shape": "—", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Thư sinh", "image": "/outfit/models/male-1.jpg", "side_image": "/outfit/models/male-1-side.jpg",
        "dossier_image": "/outfit/models/male-1.jpg", "pose_count": 2, "tagline": "Thư sinh",
        "undertone": "neutral", "height": "—", "body_shape": "—", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Vạm vỡ", "image": "/outfit/models/male-2.jpg", "side_image": "/outfit/models/male-2-side.jpg",
        "dossier_image": "/outfit/models/male-2.jpg", "pose_count": 2, "tagline": "Vạm vỡ",
        "undertone": "neutral", "height": "—", "body_shape": "—", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Lực lưỡng", "image": "/outfit/models/male-3.jpg", "side_image": "/outfit/models/male-3-side.jpg",
        "dossier_image": "/outfit/models/male-3.jpg", "pose_count": 2, "tagline": "Lực lưỡng",
        "undertone": "neutral", "height": "—", "body_shape": "—", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Mảnh khảnh", "image": "/outfit/models/male-4.jpg", "side_image": "/outfit/models/male-4-side.jpg",
        "dossier_image": "/outfit/models/male-4.jpg", "pose_count": 2, "tagline": "Mảnh khảnh",
        "undertone": "neutral", "height": "—", "body_shape": "—", "waist": "—", "personal_color": "—",
    },
]


def seed_demo_models(db: Session) -> None:
    if db.query(CatalogModel).count() > 0:
        return
    for model in DEMO_MODELS:
        db.add(CatalogModel(**model))
    db.commit()
