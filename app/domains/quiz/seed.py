from sqlalchemy.orm import Session

from app.domains.quiz.models import QuizOption, QuizQuestion

DEMO_QUIZ_QUESTIONS = [
    {
        "sort_order": 0,
        "question_text": "Tĩnh mạch ở cổ tay bạn có màu gì khi nhìn dưới ánh sáng tự nhiên?",
        "options": [
            {"label": "Xanh lá hoặc xanh ô liu", "season": "autumn"},
            {"label": "Xanh dương hoặc tím", "season": "winter"},
            {"label": "Xanh dương nhạt, khó phân biệt", "season": "summer"},
            {"label": "Xanh lá nhạt, ánh vàng", "season": "spring"},
        ],
    },
    {
        "sort_order": 1,
        "question_text": "Làn da bạn phản ứng thế nào khi ra nắng?",
        "options": [
            {"label": "Dễ cháy nắng, ít khi sạm", "season": "summer"},
            {"label": "Sạm màu nhanh, hiếm khi cháy", "season": "autumn"},
            {"label": "Rám nắng đều, khỏe khoắn", "season": "spring"},
            {"label": "Da trắng sáng, tương phản rõ khi cháy nắng", "season": "winter"},
        ],
    },
    {
        "sort_order": 2,
        "question_text": "Màu tóc tự nhiên (chưa nhuộm) của bạn gần nhất với?",
        "options": [
            {"label": "Nâu vàng, nâu hạt dẻ ánh đỏ", "season": "autumn"},
            {"label": "Đen tuyền hoặc nâu rất đậm", "season": "winter"},
            {"label": "Nâu tro, nâu hạt dẻ ánh xám", "season": "summer"},
            {"label": "Vàng óng, nâu sáng ánh vàng", "season": "spring"},
        ],
    },
    {
        "sort_order": 3,
        "question_text": "Màu mắt tự nhiên của bạn là?",
        "options": [
            {"label": "Nâu đen sắc nét", "season": "winter"},
            {"label": "Nâu hạt dẻ ấm", "season": "autumn"},
            {"label": "Nâu nhạt hoặc xám xanh dịu", "season": "summer"},
            {"label": "Nâu sáng hoặc xanh lục ánh vàng", "season": "spring"},
        ],
    },
    {
        "sort_order": 4,
        "question_text": "Khi thử trang sức, loại nào tôn da bạn hơn?",
        "options": [
            {"label": "Vàng ánh đồng, vàng ấm", "season": "autumn"},
            {"label": "Vàng nhạt, vàng hồng dịu", "season": "spring"},
            {"label": "Bạc, bạch kim sáng rõ", "season": "winter"},
            {"label": "Bạc mờ, tông pastel nhẹ", "season": "summer"},
        ],
    },
]


def seed_demo_quiz_questions(db: Session) -> None:
    if db.query(QuizQuestion).count() > 0:
        return
    for question_data in DEMO_QUIZ_QUESTIONS:
        question = QuizQuestion(
            question_text=question_data["question_text"], sort_order=question_data["sort_order"]
        )
        db.add(question)
        db.flush()
        for index, option_data in enumerate(question_data["options"]):
            db.add(
                QuizOption(
                    question_id=question.id,
                    label=option_data["label"],
                    season=option_data["season"],
                    sort_order=index,
                )
            )
    db.commit()
