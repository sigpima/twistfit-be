from sqlalchemy.orm import Session

from app.domains.team.models import TeamMember

DEMO_TEAM_MEMBERS = [
    {
        "image": "/about/team-mai-anh.jpg",
        "name": "Trần Mai Anh",
        "role": "Head of Color Science & Consulting",
        "bio": (
            "Chứng chỉ Chuyên gia Màu sắc Quốc tế (IIC). 8+ năm kinh nghiệm tư vấn định vị hình ảnh cá nhân "
            "cho các người mẫu, KOL và doanh nhân hàng đầu."
        ),
        "badge_variant": "secondary",
        "role_variant": "secondary",
        "footer_icon": "verified",
        "footer_label": "Korea Image Industry Association",
    },
    {
        "image": "/about/team-quang-huy.jpg",
        "name": "Dr. Lê Quang Huy",
        "role": "Chief Technology Officer (CTO)",
        "bio": (
            "Tiến sĩ Khoa học Máy tính tại NTU Singapore, chuyên sâu về Deep Learning và Thị giác Máy tính "
            "ứng dụng trong phân tích sắc ký ảnh kỹ thuật số."
        ),
        "badge_variant": "primary",
        "role_variant": "primary",
        "footer_icon": "memory",
        "footer_label": "5+ Sáng chế thị giác màu quang phổ",
    },
    {
        "image": "/about/team-khanh-linh.jpg",
        "name": "Nguyễn Khánh Linh",
        "role": "Creative Director & Master Stylist",
        "bio": (
            "Tốt nghiệp Học viện Thời trang London (LCA). Cựu biên tập viên phong cách cho các tạp chí "
            "phong cách sống hàng đầu, đam mê tái cấu trúc tủ đồ thông minh."
        ),
        "badge_variant": "tertiary",
        "role_variant": "tertiary",
        "footer_icon": "auto_fix_high",
        "footer_label": "Stylist của 100+ Fashion Lookbooks",
    },
]


def seed_demo_team_members(db: Session) -> None:
    if db.query(TeamMember).count() > 0:
        return
    for member in DEMO_TEAM_MEMBERS:
        db.add(TeamMember(**member))
    db.commit()
