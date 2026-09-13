from sqlalchemy.orm import Session

from app.domains.faq.models import FaqItem

DEMO_FAQ_ITEMS = [
    {
        "categories": ["personal-color"],
        "question": "Personal Color Test trên TwistFit hoạt động như thế nào qua camera?",
        "answer_markdown": (
            "Thuật toán độc quyền của TwistFit tích hợp mô hình thị giác máy tính chuyên sâu để phân tích "
            "phổ màu tự nhiên của khuôn mặt bạn theo thời gian thực.\n\n"
            "- **Định vị sắc tố:** Tách nền và nhận diện độ sáng, độ bão hòa trên da, mắt và viền môi.\n"
            "- **Đối soát Undertone:** Kiểm tra mức độ phản ứng quang phổ giữa Warm (ấm) và Cool (lạnh).\n"
            "- **Phân nhóm 16 sắc độ:** Phân loại chi tiết theo hệ 4 mùa kinh điển."
        ),
        "highlight_icon": "palette",
        "highlight_text": "Quy trình 3 bước cốt lõi.",
    },
    {
        "categories": ["personal-color"],
        "question": "Tôi cần chuẩn bị điều kiện ánh sáng và góc chụp thế nào để kết quả chính xác nhất?",
        "answer_markdown": (
            "Độ chính xác của bài kiểm tra màu phụ thuộc đáng kể vào nguồn sáng xung quanh. "
            "Chúng tôi khuyến nghị:\n\n"
            "- **Ánh sáng tự nhiên:** Chụp cạnh cửa sổ ban ngày, tránh đèn huỳnh quang vàng/trắng gắt.\n"
            "- **Mặt mộc hoàn toàn:** Tẩy trang sạch sẽ, không dùng kem chống nắng nâng tông hay kính áp tròng màu.\n"
            "- **Góc mặt chính diện:** Giữ camera ngang tầm mắt, vén tóc mái để lộ rõ trán và tai."
        ),
        "highlight_icon": "wb_sunny",
        "highlight_text": "Ánh sáng tự nhiên, mặt mộc, góc chính diện.",
    },
    {
        "categories": ["fitting-room"],
        "question": "Tính năng Thử Đồ Ảo (AI Virtual Fitting) có giữ đúng tỷ lệ vóc dáng của tôi không?",
        "answer_markdown": (
            "Hoàn toàn chính xác! Hệ thống Virtual Fitting của TwistFit sử dụng mạng nơ-ron "
            "**DensePose kết hợp 3D Neural Mesh** để tái cấu trúc hình thể người dùng từ ảnh toàn thân mà "
            "không làm biến dạng tỷ lệ chân thực.\n\n"
            "Vải của từng bộ trang phục được gán thông số vật lý riêng biệt (độ rũ của lụa, độ cứng của denim, "
            "độ bóng của da nhân tạo), giúp phản chiếu độ ôm sát và chuyển động theo đúng số đo eo, ngực và "
            "chiều dài tay chân của bạn."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["personal-color", "account"],
        "question": "Nếu dùng máy tính (Laptop/PC) thì tôi làm bài test Personal Color như thế nào?",
        "answer_markdown": (
            "Để đảm bảo chất lượng cảm biến camera tốt nhất (do webcam laptop thường có độ phân giải và cân "
            "bằng trắng thấp), TwistFit áp dụng công nghệ **Đồng Bộ Liên Màn Hình (Cross-device Sync)**: khi "
            "bắt đầu làm bài test trên màn hình lớn, một mã QR duy nhất sẽ xuất hiện. Bạn chỉ cần bật camera "
            "điện thoại quét mã để đo sắc tố, kết quả sẽ đồng bộ hiển thị ngay lập tức lên màn hình máy tính."
        ),
        "highlight_icon": "qr_code_scanner",
        "highlight_text": "Quét mã QR liền mạch.",
    },
    {
        "categories": ["account"],
        "question": "Báo cáo Personal Color sau khi test có được lưu lại không và tải về ở đâu?",
        "answer_markdown": (
            "Tất cả các lượt phân tích màu sắc và cấu trúc hình thể đều được lưu vĩnh viễn trong hồ sơ của bạn:\n\n"
            "- Truy cập menu góc phải: chọn **\"Kết quả đánh giá\"** để xem lại mọi bảng màu (Best Colors & Worst Colors).\n"
            "- Bạn có thể bấm nút **\"Xuất Báo Cáo PDF\"** để nhận cuốn cẩm nang phối đồ cá nhân hóa chuẩn tạp chí thời trang."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["account", "stylist"],
        "question": "Dữ liệu hình ảnh khuôn mặt của tôi có được bảo mật không?",
        "answer_markdown": (
            "TwistFit đặt quyền riêng tư và an toàn dữ liệu của bạn lên ưu tiên hàng đầu. Ảnh chân dung chụp "
            "qua camera chỉ được trích xuất ma trận giá trị màu (RGB/Lab) ngay trên phiên làm việc và tự động "
            "hủy sau khi tạo báo cáo. Chúng tôi không bao giờ bán, chia sẻ hoặc dùng dữ liệu khuôn mặt cho bên thứ ba."
        ),
        "highlight_icon": "verified_user",
        "highlight_text": "Chính sách không lưu trữ hình ảnh gốc thô (Raw Images).",
    },
]


def seed_demo_faq_items(db: Session) -> None:
    if db.query(FaqItem).count() > 0:
        return
    for item in DEMO_FAQ_ITEMS:
        db.add(FaqItem(**item))
    db.commit()
