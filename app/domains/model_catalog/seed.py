from sqlalchemy.orm import Session

from app.domains.model_catalog.models import CatalogModel

DEMO_MODELS = [
    {
        "name": "Dáng cao gầy", "image": "/outfit/models/female-1.jpg", "side_image": "/outfit/models/female-1-side.jpg",
        "dossier_image": "/outfit/models/female-1.jpg", "pose_count": 2,
        "tagline": "Chiều cao nổi bật, thân thanh mảnh, tay chân dài",
        "undertone": "neutral", "height": "—", "body_shape": "Cao gầy", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Dáng đầy đặn", "image": "/outfit/models/female-2.jpg", "side_image": "/outfit/models/female-2-side.jpg",
        "dossier_image": "/outfit/models/female-2.jpg", "pose_count": 2,
        "tagline": "Cân nặng cao hơn, có đường cong, mềm mại",
        "undertone": "neutral", "height": "—", "body_shape": "Đầy đặn", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Dáng đồng hồ cát", "image": "/outfit/models/female-3.jpg", "side_image": "/outfit/models/female-3-side.jpg",
        "dossier_image": "/outfit/models/female-3.jpg", "pose_count": 2,
        "tagline": "Vai và hông cân đối, eo rõ",
        "undertone": "neutral", "height": "—", "body_shape": "Đồng hồ cát", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Dáng nhỏ nhắn", "image": "/outfit/models/female-4.jpg", "side_image": "/outfit/models/female-4-side.jpg",
        "dossier_image": "/outfit/models/female-4.jpg", "pose_count": 2,
        "tagline": "Chiều cao thấp, khung xương nhỏ, thon gọn",
        "undertone": "neutral", "height": "—", "body_shape": "Nhỏ nhắn", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Dáng quả lê", "image": "/outfit/models/female-5.jpg", "side_image": "/outfit/models/female-5-side.jpg",
        "dossier_image": "/outfit/models/female-5.jpg", "pose_count": 2,
        "tagline": "Hông to hơn vai, eo rõ, đùi đầy đặn",
        "undertone": "neutral", "height": "—", "body_shape": "Quả lê", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Dáng săn chắc", "image": "/outfit/models/female-6.jpg", "side_image": "/outfit/models/female-6-side.jpg",
        "dossier_image": "/outfit/models/female-6.jpg", "pose_count": 2,
        "tagline": "Cơ bắp rõ, vai rộng, thân hình khỏe khoắn",
        "undertone": "neutral", "height": "—", "body_shape": "Săn chắc", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Dáng tam giác ngược", "image": "/outfit/models/female-7.jpg", "side_image": "/outfit/models/female-7-side.jpg",
        "dossier_image": "/outfit/models/female-7.jpg", "pose_count": 2,
        "tagline": "Vai rộng hơn hông, thân trên to hơn thân dưới",
        "undertone": "neutral", "height": "—", "body_shape": "Tam giác ngược", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Dáng thẳng", "image": "/outfit/models/female-8.jpg", "side_image": "/outfit/models/female-8-side.jpg",
        "dossier_image": "/outfit/models/female-8.jpg", "pose_count": 2,
        "tagline": "Vai, hông, eo gần như bằng nhau, ít đường cong",
        "undertone": "neutral", "height": "—", "body_shape": "Thẳng", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Dáng cao gầy", "image": "/outfit/models/male-1.jpg", "side_image": "/outfit/models/male-1-side.jpg",
        "dossier_image": "/outfit/models/male-1.jpg", "pose_count": 2,
        "tagline": "Chiều cao nổi bật, thân hình thanh mảnh",
        "undertone": "neutral", "height": "—", "body_shape": "Cao gầy", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Dáng săn chắc", "image": "/outfit/models/male-2.jpg", "side_image": "/outfit/models/male-2-side.jpg",
        "dossier_image": "/outfit/models/male-2.jpg", "pose_count": 2,
        "tagline": "Cơ bắp rõ nét, vai rộng, thân hình khỏe khoắn",
        "undertone": "neutral", "height": "—", "body_shape": "Săn chắc", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Dáng thẳng", "image": "/outfit/models/male-3.jpg", "side_image": "/outfit/models/male-3-side.jpg",
        "dossier_image": "/outfit/models/male-3.jpg", "pose_count": 2,
        "tagline": "Vai, eo, hông cân đối, ít cơ bắp nổi rõ",
        "undertone": "neutral", "height": "—", "body_shape": "Thẳng", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Dáng nhỏ nhắn", "image": "/outfit/models/male-4.jpg", "side_image": "/outfit/models/male-4-side.jpg",
        "dossier_image": "/outfit/models/male-4.jpg", "pose_count": 2,
        "tagline": "Chiều cao khiêm tốn, khung người gọn gàng",
        "undertone": "neutral", "height": "—", "body_shape": "Nhỏ nhắn", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Dáng cân đối", "image": "/outfit/models/male-5.jpg", "side_image": "/outfit/models/male-5-side.jpg",
        "dossier_image": "/outfit/models/male-5.jpg", "pose_count": 2,
        "tagline": "Tỷ lệ cơ thể hài hòa, không quá gầy hay quá cơ bắp",
        "undertone": "neutral", "height": "—", "body_shape": "Cân đối", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Dáng đầy đặn", "image": "/outfit/models/male-6.jpg", "side_image": "/outfit/models/male-6-side.jpg",
        "dossier_image": "/outfit/models/male-6.jpg", "pose_count": 2,
        "tagline": "Thân hình đầy đặn, mềm mại",
        "undertone": "neutral", "height": "—", "body_shape": "Đầy đặn", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Dáng vạm vỡ", "image": "/outfit/models/male-7.jpg", "side_image": "/outfit/models/male-7-side.jpg",
        "dossier_image": "/outfit/models/male-7.jpg", "pose_count": 2,
        "tagline": "Thân hình to bản, vai ngực rộng",
        "undertone": "neutral", "height": "—", "body_shape": "Vạm vỡ", "waist": "—", "personal_color": "—",
    },
    {
        "name": "Dáng mảnh khảnh", "image": "/outfit/models/male-8.jpg", "side_image": "/outfit/models/male-8-side.jpg",
        "dossier_image": "/outfit/models/male-8.jpg", "pose_count": 2,
        "tagline": "Chiều cao nổi bật, thân hình mảnh khảnh",
        "undertone": "neutral", "height": "—", "body_shape": "Mảnh khảnh", "waist": "—", "personal_color": "—",
    },
]


def seed_demo_models(db: Session) -> None:
    if db.query(CatalogModel).count() > 0:
        return
    for model in DEMO_MODELS:
        db.add(CatalogModel(**model))
    db.commit()
