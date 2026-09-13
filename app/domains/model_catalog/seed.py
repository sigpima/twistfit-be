from sqlalchemy.orm import Session

from app.domains.model_catalog.models import CatalogModel

DEMO_MODELS = [
    {
        "name": "Carmen", "image": "/outfit/models/carmen-card.jpg", "dossier_image": "/outfit/models/carmen-dossier.jpg",
        "pose_count": 15, "tagline": "Tông da: Warm Neutral", "undertone": "neutral", "height": "1m65",
        "body_shape": "Đồng hồ cát", "waist": "64cm", "personal_color": "Autumn Soft",
    },
    {
        "name": "Aisha", "image": "/outfit/models/aisha.jpg", "dossier_image": "/outfit/models/aisha.jpg",
        "pose_count": 15, "tagline": "Da ngăm • Warm Deep", "undertone": "warm", "height": "1m70",
        "body_shape": "Đồng hồ cát", "waist": "66cm", "personal_color": "Warm Deep Autumn",
    },
    {
        "name": "Alice", "image": "/outfit/models/alice.jpg", "dossier_image": "/outfit/models/alice.jpg",
        "pose_count": 15, "tagline": "Da sáng • Cool Summer", "undertone": "cool", "height": "1m68",
        "body_shape": "Dáng thước kẻ", "waist": "62cm", "personal_color": "Cool Summer Light",
    },
    {
        "name": "Amara", "image": "/outfit/models/amara.jpg", "dossier_image": "/outfit/models/amara.jpg",
        "pose_count": 15, "tagline": "Afro Chic • Tôn đồ màu", "undertone": "warm", "height": "1m72",
        "body_shape": "Đồng hồ cát", "waist": "68cm", "personal_color": "Warm Spring Bright",
    },
    {
        "name": "Arjun", "image": "/outfit/models/arjun.jpg", "dossier_image": "/outfit/models/arjun.jpg",
        "pose_count": 12, "tagline": "Mẫu nam • Form Unisex", "undertone": "neutral", "height": "1m80",
        "body_shape": "Chữ nhật", "waist": "80cm", "personal_color": "Neutral Autumn",
    },
    {
        "name": "Astrid", "image": "/outfit/models/astrid.jpg", "dossier_image": "/outfit/models/astrid.jpg",
        "pose_count": 15, "tagline": "Tây Âu • Dáng thanh mảnh", "undertone": "cool", "height": "1m75",
        "body_shape": "Dáng thước kẻ", "waist": "60cm", "personal_color": "Cool Winter Bright",
    },
    {
        "name": "Chloe", "image": "/outfit/models/chloe.jpg", "dossier_image": "/outfit/models/chloe.jpg",
        "pose_count": 15, "tagline": "Á Đông • Dáng Petite", "undertone": "neutral", "height": "1m58",
        "body_shape": "Petite", "waist": "58cm", "personal_color": "Neutral Spring",
    },
    {
        "name": "Bella", "image": "/outfit/models/bella.jpg", "dossier_image": "/outfit/models/bella.jpg",
        "pose_count": 15, "tagline": "Đồng hồ cát • Đầy đặn", "undertone": "warm", "height": "1m67",
        "body_shape": "Đồng hồ cát", "waist": "70cm", "personal_color": "Warm Autumn Deep",
    },
    {
        "name": "Camille", "image": "/outfit/models/camille.jpg", "dossier_image": "/outfit/models/camille.jpg",
        "pose_count": 15, "tagline": "Parisian Chic • Dáng Quả Lê", "undertone": "neutral", "height": "1m66",
        "body_shape": "Quả lê", "waist": "65cm", "personal_color": "Neutral Summer",
    },
    {
        "name": "Dave", "image": "/outfit/models/dave.jpg", "dossier_image": "/outfit/models/dave.jpg",
        "pose_count": 10, "tagline": "Mẫu nam • Dáng thể thao", "undertone": "warm", "height": "1m82",
        "body_shape": "Thể thao", "waist": "82cm", "personal_color": "Warm Spring",
    },
    {
        "name": "Linh Đan", "image": "/outfit/models/linh-dan.jpg", "dossier_image": "/outfit/models/linh-dan.jpg",
        "pose_count": 15, "tagline": "Thuần Việt • Da trắng hồng", "undertone": "cool", "height": "1m62",
        "body_shape": "Đồng hồ cát", "waist": "60cm", "personal_color": "Cool Summer Soft",
    },
    {
        "name": "Kenji", "image": "/outfit/models/kenji.jpg", "dossier_image": "/outfit/models/kenji.jpg",
        "pose_count": 12, "tagline": "Tokyo Street • Tối giản", "undertone": "cool", "height": "1m75",
        "body_shape": "Chữ nhật", "waist": "76cm", "personal_color": "Cool Winter Deep",
    },
]


def seed_demo_models(db: Session) -> None:
    if db.query(CatalogModel).count() > 0:
        return
    for model in DEMO_MODELS:
        db.add(CatalogModel(**model))
    db.commit()
