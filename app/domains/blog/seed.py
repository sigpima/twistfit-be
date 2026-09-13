from sqlalchemy.orm import Session

from app.domains.blog.models import BlogPost

DEMO_BLOG_POSTS = [
    {
        "slug": "bi-quyet-chon-trang-phuc-ton-da-mua-dong-2026",
        "title": "Bí quyết chọn trang phục tôn da chuẩn tone Mùa Đông - Xu hướng mới nhất 2026",
        "excerpt": (
            "Khám phá sức hút mãnh liệt của sự tương phản cao và cách kết hợp trang phục lạnh sáng sắc nét "
            "giúp tôn vinh thần thái tự nhiên, đánh bật mọi khung hình."
        ),
        "content": (
            "Khám phá sức hút mãnh liệt của sự tương phản cao và cách kết hợp trang phục lạnh sáng sắc nét "
            "giúp tôn vinh thần thái tự nhiên, đánh bật mọi khung hình."
        ),
        "cover_image_url": "/blog/featured-winter-outfit.jpg",
        "category": "personal-color",
        "author_name": "Stylist Mai Anh",
        "is_featured": True,
        "published_at": "2026-06-18",
    },
    {
        "slug": "top-5-thoi-son-cool-undertone",
        "title": "Top 5 thỏi son kinh điển dành riêng cho cô nàng thuộc nhóm Cool Undertone",
        "excerpt": (
            "Sự thanh khiết và dịu mát của tone Mùa Hạ đến sắc son có sắc hồng dịu, tím sữa hoặc berry nhẹ "
            "để đôi môi luôn ửng hồng tự nhiên mà không bị già."
        ),
        "content": (
            "Sự thanh khiết và dịu mát của tone Mùa Hạ đến sắc son có sắc hồng dịu, tím sữa hoặc berry nhẹ "
            "để đôi môi luôn ửng hồng tự nhiên mà không bị già."
        ),
        "cover_image_url": "/blog/lipstick-flatlay.jpg",
        "category": "beauty",
        "author_name": None,
        "is_featured": False,
        "published_at": "2026-06-18",
    },
    {
        "slug": "tu-do-con-nhong-30-mon",
        "title": "Tủ đồ con nhộng (Capsule Wardrobe): Tối ưu 30 món mặc đẹp quanh năm",
        "excerpt": (
            "Hướng dẫn chi tiết từng bước thanh lọc trang phục lỗi thời, tập trung vào những món đồ bền "
            "vững có tính ứng dụng cao và chuẩn sắc thái cá nhân."
        ),
        "content": (
            "Hướng dẫn chi tiết từng bước thanh lọc trang phục lỗi thời, tập trung vào những món đồ bền "
            "vững có tính ứng dụng cao và chuẩn sắc thái cá nhân."
        ),
        "cover_image_url": "/blog/capsule-wardrobe-rail.jpg",
        "category": "sustainable",
        "author_name": None,
        "is_featured": False,
        "published_at": "2026-05-09",
    },
    {
        "slug": "doi-quan-ao-cu-nhan-phan-tich-mau-mien-phi",
        "title": "Chiến dịch 'Đổi Quần Áo Cũ - Nhận Bản Phân Tích Màu Sắc Miễn Phí'",
        "excerpt": (
            "Chung tay cùng TwistFit giảm thiểu rác thải thời trang dệt may, mang lại vòng đời mới cho "
            "trang phục và nâng cấp gu ăn mặc của chính bạn."
        ),
        "content": (
            "Chung tay cùng TwistFit giảm thiểu rác thải thời trang dệt may, mang lại vòng đời mới cho "
            "trang phục và nâng cấp gu ăn mặc của chính bạn."
        ),
        "cover_image_url": "/blog/community-swap.jpg",
        "category": "community",
        "author_name": None,
        "is_featured": False,
        "published_at": "2026-05-06",
    },
    {
        "slug": "nhan-biet-warm-cool-undertone-tai-nha",
        "title": "Cách nhận biết Warm Undertone vs Cool Undertone chính xác tại nhà chỉ trong 1 phút",
        "excerpt": (
            "Chỉ với ánh sáng tự nhiên và vài mẹo quan sát mạch máu hoặc trang sức vàng bạc, bạn hoàn toàn "
            "có thể tự kiểm tra sắc thái da cơ bản."
        ),
        "content": (
            "Chỉ với ánh sáng tự nhiên và vài mẹo quan sát mạch máu hoặc trang sức vàng bạc, bạn hoàn toàn "
            "có thể tự kiểm tra sắc thái da cơ bản."
        ),
        "cover_image_url": "/blog/undertone-draping.jpg",
        "category": "personal-color",
        "author_name": None,
        "is_featured": False,
        "published_at": "2026-04-28",
    },
    {
        "slug": "phoi-layer-ton-dang-lung-dai-chan-ngan",
        "title": "Bí kíp phối layer tôn dáng cho người có tỷ lệ lưng dài chân ngắn",
        "excerpt": (
            "Tận dụng độ cạp cao của quần âu, áo croptop lửng và sự tương phản màu sắc giúp 'hack' chiều "
            "cao hiệu quả trên tính năng thử đồ ảo TwistFit."
        ),
        "content": (
            "Tận dụng độ cạp cao của quần âu, áo croptop lửng và sự tương phản màu sắc giúp 'hack' chiều "
            "cao hiệu quả trên tính năng thử đồ ảo TwistFit."
        ),
        "cover_image_url": "/blog/proportion-styling-flatlay.jpg",
        "category": "styling",
        "author_name": None,
        "is_featured": False,
        "published_at": "2026-04-20",
    },
    {
        "slug": "bang-mau-mua-thu-am-ap",
        "title": "Sức hút ấm áp từ bảng màu Mùa Thu (Autumn Warm): Khi tone đất lên ngôi",
        "excerpt": (
            "Những gam màu nâu caramel, cam cháy và rêu olive mang đến sự quý phái, đằm thắm cho những "
            "buổi hẹn hò hoặc sự kiện trang trọng."
        ),
        "content": (
            "Những gam màu nâu caramel, cam cháy và rêu olive mang đến sự quý phái, đằm thắm cho những "
            "buổi hẹn hò hoặc sự kiện trang trọng."
        ),
        "cover_image_url": "/blog/autumn-palette-moodboard.jpg",
        "category": "personal-color",
        "author_name": None,
        "is_featured": False,
        "published_at": "2026-04-12",
    },
]


def seed_demo_blog_posts(db: Session) -> None:
    if db.query(BlogPost).count() > 0:
        return
    for post in DEMO_BLOG_POSTS:
        db.add(BlogPost(**post))
    db.commit()
