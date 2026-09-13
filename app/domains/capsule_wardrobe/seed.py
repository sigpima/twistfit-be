from sqlalchemy.orm import Session

from app.domains.capsule_wardrobe.models import CapsuleSet

DEMO_CAPSULE_SETS = [
    {
        "image": "/outfit/capsule-set-office.jpg",
        "alt": "Set đồ công sở thanh lịch với áo peplum hồng, quần ống suông trắng ngà và túi xách minimalist",
        "tag_variant": "primary",
        "tag_label": "Set 1 • Thanh Lịch",
        "fit_for": "Phù hợp: Office & Meeting",
        "title": "Thanh Lịch Công Sở",
        "tone": "Warm Cream",
        "description": (
            "Áo Peplum Voan Hồng + Quần Ống Suông Trắng Ngà + Túi xách Minimalist. Tối ưu chiều dài chân và "
            "tạo nét chuyên nghiệp, nhã nhặn."
        ),
        "items": [
            {"label": "Quần ống suông ngà:", "price": "490.000 ₫"},
            {"label": "Túi xách Minimalist:", "price": "720.000 ₫"},
        ],
    },
    {
        "image": "/outfit/capsule-set-date.jpg",
        "alt": "Set đồ dạo phố với áo peplum hồng, chân váy midi xám bạc và giày slingback",
        "tag_variant": "secondary",
        "tag_label": "Set 2 • Dạo Phố",
        "fit_for": "Phù hợp: Dating & Weekend",
        "title": "Hẹn Hò & Dạo Phố",
        "tone": "Soft Silver",
        "description": (
            "Áo Peplum + Chân Váy Xòe Midi Xám Bạc tôn vẻ nữ tính dịu dàng. Màu xám bạc lạnh làm nổi bật sắc "
            "hồng thanh khiết của áo."
        ),
        "items": [
            {"label": "Chân váy midi xám bạc:", "price": "530.000 ₫"},
            {"label": "Giày Slingback Satin:", "price": "650.000 ₫"},
        ],
    },
    {
        "image": "/outfit/capsule-set-accessories.jpg",
        "alt": "Phụ kiện khuyên tai bạc và túi pastel lilac bổ trợ cho set đồ",
        "tag_variant": "tertiary",
        "tag_label": "Set 3 • Điểm Nhấn",
        "fit_for": "Phù hợp: Điểm Nhấn Cao Cấp",
        "title": "Phụ Kiện Tối Ưu",
        "tone": "Pastel Lilac",
        "description": (
            "Khuyên Tai Bạc Silver + Túi Pastel Lilac ánh tím. Bổ trợ hoàn hảo cho nhóm màu Summer Soft mà "
            "không làm lu mờ sắc áo chính."
        ),
        "items": [
            {"label": "Khuyên tai bạc Ý 925:", "price": "320.000 ₫"},
            {"label": "Túi Pastel Lilac:", "price": "580.000 ₫"},
        ],
    },
]


def seed_demo_capsule_sets(db: Session) -> None:
    if db.query(CapsuleSet).count() > 0:
        return
    for capsule_set in DEMO_CAPSULE_SETS:
        db.add(CapsuleSet(**capsule_set))
    db.commit()
