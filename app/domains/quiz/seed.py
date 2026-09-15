from sqlalchemy.orm import Session

from app.domains.quiz.models import QuizOption, QuizQuestion

DEMO_QUIZ_QUESTIONS = [
    {
        "sort_order": 0,
        "axis": "hue",
        "image_url": "/personal-color/quiz/wrist-veins.jpg",
        "question_text": "Hãy nhìn vào tĩnh mạch ở cổ tay dưới ánh sáng tự nhiên. Chúng nghiêng về màu gì?",
        "options": [
            {"label": "Xanh lá / Olive", "axis_value": "warm"},
            {"label": "Xanh dương / Tím", "axis_value": "cool"},
            {"label": "Lẫn lộn khó phân biệt", "axis_value": "neutral"},
        ],
    },
    {
        "sort_order": 1,
        "axis": "hue",
        "image_url": None,
        "question_text": "Đặt một tờ giấy bạc và giấy vàng (hoặc trang sức vàng/bạc) kề sát mặt. Loại nào làm da bạn sáng hơn?",
        "options": [
            {"label": "Vàng nguyên bản (Gold)", "axis_value": "warm"},
            {"label": "Bạc / Bạch kim (Silver)", "axis_value": "cool"},
            {"label": "Cả hai đều hài hòa", "axis_value": "neutral"},
        ],
    },
    {
        "sort_order": 2,
        "axis": "hue",
        "image_url": None,
        "question_text": "Khi tiếp xúc lâu với nắng gắt, da bạn phản ứng thế nào?",
        "options": [
            {"label": "Nhanh chóng rám nắng, sạm đen", "axis_value": "warm"},
            {"label": "Dễ ửng đỏ, cháy rát", "axis_value": "cool"},
            {"label": "Ửng đỏ nhẹ rồi mới chuyển rám", "axis_value": "neutral"},
        ],
    },
    {
        "sort_order": 3,
        "axis": "hue",
        "image_url": None,
        "question_text": "Cầm một tờ giấy trắng tinh kề cạnh mặt. So với tờ giấy, da bạn ánh lên màu gì?",
        "options": [
            {"label": "Ánh vàng / Cam (Yellowish/Golden)", "axis_value": "warm"},
            {"label": "Ánh hồng / Đỏ (Pinkish/Rosy)", "axis_value": "cool"},
            {"label": "Không rõ ràng (No strong leaning)", "axis_value": "neutral"},
        ],
    },
    {
        "sort_order": 4,
        "axis": "value",
        "image_url": None,
        "question_text": "Màu tóc tự nhiên của bạn là màu gì?",
        "options": [
            {"label": "Đen láy / Nâu cực đậm", "axis_value": "dark"},
            {"label": "Nâu sáng / Hạt dẻ", "axis_value": "light"},
            {"label": "Nâu trung bình", "axis_value": "medium"},
        ],
    },
    {
        "sort_order": 5,
        "axis": "value",
        "image_url": None,
        "question_text": "Màu tròng đen của mắt bạn nghiêng về phổ màu nào?",
        "options": [
            {"label": "Đen / Nâu rất đậm, sâu thẳm", "axis_value": "dark"},
            {"label": "Nâu sáng / Hổ phách, trong trẻo", "axis_value": "light"},
            {"label": "Nâu trung bình", "axis_value": "medium"},
        ],
    },
    {
        "sort_order": 6,
        "axis": "value",
        "image_url": None,
        "question_text": "Nhìn vào ảnh mặt mộc, sự chênh lệch (tương phản) giữa Tóc - Da - Mắt của bạn thế nào? (Chụp ảnh và chỉnh thành màu đen trắng sẽ dễ xác định hơn)",
        "options": [
            {"label": "Rất rõ (Tóc sẫm nổi bật trên nền da)", "axis_value": "dark"},
            {"label": "Thấp (Tóc, da, mắt gần màu nhau, hòa quyện)", "axis_value": "light"},
            {"label": "Trung bình", "axis_value": "medium"},
        ],
    },
    {
        "sort_order": 7,
        "axis": "chroma",
        "image_url": None,
        "question_text": "Khi mặc màu rực rỡ (Đỏ tươi, Xanh cobalt, Vàng chanh), khuôn mặt bạn trông thế nào?",
        "options": [
            {"label": "Bừng sáng, sắc nét và nổi bật hẳn lên", "axis_value": "bright"},
            {"label": "Bị màu áo lấn át, da nhợt nhạt/tối sầm", "axis_value": "muted"},
            {"label": "Bình thường", "axis_value": "neutral"},
        ],
    },
    {
        "sort_order": 8,
        "axis": "chroma",
        "image_url": None,
        "question_text": "Khi mặc màu trầm khói (Hồng đất, Rêu xám, Nâu be), bạn thấy thế nào?",
        "options": [
            {"label": "Nhợt nhạt, già đi và thiếu sức sống", "axis_value": "bright"},
            {"label": "Rất sang trọng, hài hòa và tôn da", "axis_value": "muted"},
            {"label": "Bình thường", "axis_value": "neutral"},
        ],
    },
    {
        "sort_order": 9,
        "axis": "hue",
        "image_url": None,
        "question_text": "Nhóm màu nào bạn mặc và được khen nhiều nhất?",
        "options": [
            {"label": "Ấm: Cam đào, Vàng ấm, Nâu đất, Rêu", "axis_value": "warm"},
            {"label": "Lạnh: Hồng pastel, Xanh baby, Đỏ cherry, Navy", "axis_value": "cool"},
            {"label": "Bình thường", "axis_value": "neutral"},
        ],
    },
]


def seed_demo_quiz_questions(db: Session) -> None:
    if db.query(QuizQuestion).count() > 0:
        return
    for question_data in DEMO_QUIZ_QUESTIONS:
        question = QuizQuestion(
            question_text=question_data["question_text"],
            axis=question_data["axis"],
            image_url=question_data["image_url"],
            sort_order=question_data["sort_order"],
        )
        db.add(question)
        db.flush()
        for index, option_data in enumerate(question_data["options"]):
            db.add(
                QuizOption(
                    question_id=question.id,
                    label=option_data["label"],
                    axis_value=option_data["axis_value"],
                    sort_order=index,
                )
            )
    db.commit()
