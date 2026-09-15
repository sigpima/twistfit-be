from sqlalchemy.orm import Session

from app.domains.faq.models import FaqItem

DEMO_FAQ_ITEMS = [
    {
        "categories": ["account"],
        "question": "Tôi không nhận được mã xác thực (OTP) hoặc email kích hoạt thì phải làm sao?",
        "answer_markdown": (
            "Hãy kiểm tra kỹ hòm thư rác/spam. Nếu vẫn chưa nhận được sau 1–2 phút, bạn bấm nút "
            '"Gửi lại mã" hoặc kiểm tra lại độ chính xác của địa chỉ email/số điện thoại đã nhập.'
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["account"],
        "question": "Tôi quên mật khẩu thì lấy lại bằng cách nào?",
        "answer_markdown": (
            'Chọn "Quên mật khẩu" tại màn hình đăng nhập, điền email đăng ký tài khoản và làm theo '
            "hướng dẫn trong link vừa được gửi tới hộp thư của bạn."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["account"],
        "question": "Kết quả đánh giá màu sắc cá nhân và dữ liệu tủ đồ ảo có bị mất khi tôi đăng xuất không?",
        "answer_markdown": (
            "Không. Mọi dữ liệu về tủ đồ, kết quả trắc nghiệm và lịch sử phối đồ đều được tự động lưu "
            "trữ an toàn trên hệ thống máy chủ gắn liền với tài khoản của bạn."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["account"],
        "question": (
            "Điều gì sẽ xảy ra với hình ảnh trang phục và kết quả đánh giá màu sắc cá nhân khi tôi "
            "xóa tài khoản?"
        ),
        "answer_markdown": (
            "Toàn bộ ảnh tủ đồ, lịch sử phối đồ, bài viết trên diễn đàn và kết quả đánh giá màu sắc "
            "cá nhân của bạn sẽ bị xóa vĩnh viễn khỏi hệ thống máy chủ và không thể khôi phục lại."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["account"],
        "question": "Tôi có thể dùng website trên điện thoại (giao diện di động) mượt mà không?",
        "answer_markdown": (
            "Hoàn toàn được. Trang web được tối ưu hóa hiển thị trên mọi trình duyệt điện thoại "
            "(iOS và Android), giúp bạn chụp ảnh tải đồ lên và kiểm tra màu sắc cá nhân mọi lúc mọi nơi."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["account"],
        "question": "Tôi có thể đăng nhập cùng một tài khoản trên nhiều thiết bị (điện thoại, máy tính) không?",
        "answer_markdown": (
            "Có. Dữ liệu tủ đồ và kết quả đánh giá của bạn sẽ tự động đồng bộ hóa trên mọi thiết bị "
            "khi bạn đăng nhập cùng một tài khoản."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["account"],
        "question": (
            "Tôi có thể cập nhật lại các chỉ số cơ thể (chiều cao, cân nặng, dáng người) trong tài "
            "khoản không?"
        ),
        "answer_markdown": (
            "Có. Bạn vào mục Hồ sơ cá nhân > chọn Thông tin cá nhân, cập nhật lại số đo mới và bấm "
            "Lưu thay đổi."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["personal-color"],
        "question": "Màu sắc cá nhân là gì?",
        "answer_markdown": (
            "Màu sắc cá nhân (Personal Color) là phương pháp phân tích màu sắc dựa trên sắc độ da, "
            "màu tóc, màu mắt và độ tương phản tự nhiên của gương mặt để tìm ra những gam màu phù hợp "
            "nhất với mỗi người. Thay vì lựa chọn màu sắc chỉ theo xu hướng, màu sắc cá nhân giúp xác "
            "định bảng màu riêng có khả năng làm nổi bật diện mạo, từ trang phục, phụ kiện đến phong "
            "cách trang điểm."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["personal-color"],
        "question": "Màu sắc cá nhân có thay đổi theo thời gian không?",
        "answer_markdown": (
            "Undertone da thường không thay đổi, vì vậy nhóm màu sắc cá nhân cơ bản của mỗi người "
            "thường giữ nguyên. Tuy nhiên, cảm nhận về màu sắc phù hợp có thể thay đổi do màu tóc, "
            "phong cách trang điểm, độ rám nắng hoặc sự thay đổi trong cách xây dựng hình ảnh cá nhân."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["personal-color"],
        "question": "Biết màu sắc cá nhân mang lại lợi ích gì cho phong cách và diện mạo của tôi?",
        "answer_markdown": (
            "Thấu hiểu màu sắc cá nhân là chìa khóa giúp bạn dễ dàng chọn lựa trang phục tôn lên diện "
            "mạo, đồng thời tránh lãng phí vào những xu hướng không phù hợp. Đây không chỉ là nền "
            "tảng giúp bạn chọn trang phục tôn da và xây dựng tủ đồ bền vững, mà còn hỗ trợ chọn màu "
            "tóc, màu son trang điểm và phụ kiện hài hòa nhất với gương mặt."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["personal-color"],
        "question": "Bài đánh giá màu sắc cá nhân trên website hoạt động như thế nào?",
        "answer_markdown": (
            "Bài đánh giá được thiết kế liền mạch theo quy trình 3 bước:\n\n"
            "**Bước 1: Phân tích đặc điểm tự nhiên**\n"
            "Hệ thống sử dụng thuật toán thông minh để phân tích các yếu tố sắc tố da, mạch máu cổ "
            "tay, màu mắt và tóc thông qua bộ câu hỏi trắc nghiệm, từ đó xác định nhóm mùa chuyên sâu "
            "(Xuân - Hạ - Thu - Đông) của bạn.\n\n"
            "**Bước 2: Ướm thử trực quan với AR Draping**\n"
            "Ngay sau khi có kết quả, công nghệ thực tế ảo sẽ kích hoạt camera để bạn ướm trực tiếp "
            "các dải màu thuộc nhóm mùa đó lên gương mặt theo thời gian thực, giúp bạn tự kiểm chứng "
            "độ sáng và độ hòa hợp của làn da.\n\n"
            "**Bước 3: Đề xuất gợi ý ứng dụng**\n"
            "Dựa trên nhóm màu đã xác định, hệ thống cung cấp các gợi ý ứng dụng đa dạng giúp bạn dễ "
            "dàng khai thác tối đa bảng màu cá nhân vào trang phục, làm đẹp và định hình phong cách "
            "hàng ngày."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["personal-color"],
        "question": "Bài đánh giá màu sắc cá nhân có độ chính xác cao không?",
        "answer_markdown": (
            "Bài đánh giá cung cấp định hướng chính xác từ 70% - 80% dựa trên sự quan sát thực tế "
            "của bạn. Đây là công cụ hỗ trợ miễn phí để bạn bắt đầu định hình phong cách cá nhân "
            "trước khi quyết định tư vấn trực tiếp với chuyên gia."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["personal-color"],
        "question": "Làm sao để tôi phân biệt Undertone (sắc tố da) và Skintone (màu da)?",
        "answer_markdown": (
            "**Skintone**: Là màu da bề mặt mà bạn nhìn thấy bằng mắt thường (trắng, ngăm, trung "
            "tính...), có thể thay đổi theo thời gian, mùa trong năm hoặc chịu ảnh hưởng từ yếu tố "
            "môi trường và thói quen chăm sóc da.\n\n"
            "**Undertone**: Là sắc tố ẩn dưới bề mặt da, khác với skintone - màu da bạn nhìn thấy "
            "bằng mắt thường. Trong khi skintone có thể thay đổi theo thời tiết, ánh nắng hay chế độ "
            "chăm sóc da, Undertone lại ổn định và không thay đổi theo thời gian. Bài quiz sẽ tập "
            "trung xác định Undertone của bạn."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["personal-color"],
        "question": "Tôi có cần phải bỏ hết quần áo cũ không hợp với màu sắc cá nhân không?",
        "answer_markdown": (
            "Hoàn toàn không cần thiết. Bạn vẫn có thể mặc những màu mình yêu thích bằng các mẹo "
            "nhỏ:\n\n"
            "- Kết hợp màu không hợp ở phần thân dưới (quần, chân váy) xa khuôn mặt.\n"
            "- Sử dụng phụ kiện, khăn quàng hoặc tone trang điểm chuẩn Màu sắc cá nhân để cân bằng "
            "lại tổng thể."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["personal-color"],
        "question": "Bài đánh giá màu sắc cá nhân có mất phí không và tôi có thể thực hiện lại không?",
        "answer_markdown": (
            "Bài đánh giá màu sắc cá nhân trên website của chúng tôi hoàn toàn MIỄN PHÍ và KHÔNG "
            "GIỚI HẠN LƯỢT LÀM. Bạn có thể thực hiện bất cứ lúc nào và lưu lại kết quả."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["fitting-room"],
        "question": "Tính năng Phối đồ AI dựa trên tủ đồ cá nhân là gì?",
        "answer_markdown": (
            "Đây là trợ lý thời trang ảo sử dụng trí tuệ nhân tạo để phân tích các món đồ bạn đã tải "
            "lên (áo, quần, váy, giày, phụ kiện...) và tự động kết hợp chúng thành những outfit hoàn "
            "chỉnh, phù hợp với yêu cầu (dịp mặc, phong cách,...) của bạn."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["fitting-room"],
        "question": "Tôi cần tải ảnh trang phục như thế nào để AI nhận diện tốt nhất?",
        "answer_markdown": (
            "Để AI phân tích chính xác nhất, bạn nên:\n\n"
            "- Chụp riêng từng món đồ trên nền trơn (như sàn nhà, ga giường trắng) hoặc treo trên "
            "móc.\n"
            "- Chụp trong điều kiện đủ ánh sáng tự nhiên.\n"
            "- Tránh chụp chung nhiều món đồ trong một bức ảnh hoặc chụp người đang mặc đồ nếu có "
            "quá nhiều chi tiết rối mắt."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["fitting-room"],
        "question": "Có giới hạn số lượng món đồ tôi được phép tải lên không?",
        "answer_markdown": "Không, bạn có thể tải lên số lượng đồ tùy ý.",
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["fitting-room"],
        "question": "AI dựa vào những yếu tố nào để gợi ý outfit, và tôi có thể tùy chỉnh theo dịp không?",
        "answer_markdown": (
            "Hệ thống sẽ lấy toàn bộ trang phục sẵn có trong tủ đồ ảo của bạn làm dữ liệu gốc, kết "
            "hợp với các tiêu chí tùy chỉnh do bạn chọn:\n\n"
            "- **Bối cảnh & Phong cách**: Lọc theo dịp mặc cụ thể (đi làm, dạo phố, dự tiệc, thể "
            "thao...) và phong cách bạn mong muốn.\n"
            "- **Bảng màu cá nhân**: Tự động ưu tiên các món đồ chuẩn màu sắc cá nhân nếu bạn đã "
            "hoàn thành bài đánh giá trước đó.\n"
            "- **Gợi ý món đồ bổ sung**: Nếu outfit sẵn có cần thêm điểm nhấn, AI có thể gợi ý thêm "
            "1 món đồ ngoài (kèm link mua sản phẩm tham khảo) để hoàn thiện set đồ chỉn chu hơn."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["fitting-room"],
        "question": "Tính năng này có liên kết với kết quả đánh giá màu sắc cá nhân không?",
        "answer_markdown": (
            "Có. Nếu bạn đã thực hiện bài đánh giá màu sắc cá nhân trên trang website và chọn ô "
            '"Phối đồ theo kết quả đánh giá màu sắc cá nhân", AI sẽ ưu tiên chọn các món đồ có màu '
            "sắc chuẩn với bảng màu cá nhân để phối thành outfit hoàn chỉnh."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["fitting-room"],
        "question": "Hình ảnh tủ đồ cá nhân của tôi có được bảo mật không?",
        "answer_markdown": (
            "Tuyệt đối bảo mật. Toàn bộ hình ảnh và dữ liệu tủ đồ chỉ phục vụ cho tài khoản cá nhân "
            "của bạn. Chúng tôi cam kết không công khai hay sử dụng hình ảnh của bạn cho bất kỳ mục "
            "đích nào khác mà không có sự đồng ý."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["fitting-room"],
        "question": "Tôi có thể chỉnh sửa thông tin nếu AI phân loại sai món đồ không?",
        "answer_markdown": (
            "Có. Sau khi tải ảnh lên, AI sẽ tự động phân loại loại trang phục. Bạn hoàn toàn có thể "
            "chỉnh sửa lại các thông tin này thủ công bất cứ lúc nào để dữ liệu chính xác nhất."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["fitting-room"],
        "question": "Nếu không thích outfit được gợi ý, tôi phải làm gì?",
        "answer_markdown": (
            'Bạn chỉ cần nhấn nút "Đổi gợi ý khác". AI sẽ ngay lập tức tạo ra kết hợp mới. Dựa vào '
            "các lịch sử hoạt động của bạn, AI sẽ hiểu rõ hơn gu thẩm mỹ của bạn để đưa ra gợi ý "
            "chuẩn xác hơn trong tương lai."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["fitting-room"],
        "question": "Mất bao lâu để AI tạo xong các gợi ý phối đồ?",
        "answer_markdown": (
            "Tốc độ xử lý siêu nhanh. Hệ thống chỉ mất từ 3 đến 5 giây để quét toàn bộ tủ đồ của bạn "
            "và đưa ra hàng loạt công thức phối đồ sẵn sàng."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["policy"],
        "question": "Thông tin trong hồ sơ cá nhân của tôi có hiển thị với người dùng khác không?",
        "answer_markdown": (
            "Không. Mọi thông tin cơ bản trong hồ sơ cá nhân (email, số đo cơ thể, chiều cao, cân "
            "nặng và các dữ liệu tài khoản cá nhân khác) hoàn toàn bảo mật và không hiển thị công "
            "khai cho bất kỳ ai."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["policy"],
        "question": "Ai có thể xem bài viết và hình ảnh Cộng đồng của tôi?",
        "answer_markdown": (
            "Bất kỳ người dùng nào trên nền tảng TwistFit đều có thể xem các nội dung bạn công khai "
            "đăng tải lên bảng tin hoặc bình luận."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["policy"],
        "question": "TwistFit thu thập hình ảnh của tôi nhằm mục đích gì?",
        "answer_markdown": (
            "Hình ảnh từ camera AR được áp dụng trong bài đánh giá màu sắc cá nhân chỉ được xử lý "
            "theo thời gian thực nhằm phục vụ trải nghiệm ướm thử dải màu và lưu lại 01 ảnh kết quả "
            "vào Hồ sơ cá nhân khi bạn xác nhận. Đối với hình ảnh đăng tải trên Diễn đàn, hệ thống "
            "lưu trữ để hiển thị bài đăng/bình luận theo ý muốn của bạn."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["policy"],
        "question": "Hình ảnh từ camera AR khi đánh giá màu sắc cá nhân có bị lưu trữ lâu dài không?",
        "answer_markdown": (
            "Không. Trải nghiệm thử màu qua công nghệ thực tế ảo được xử lý trực tiếp theo thời gian "
            "thực ngay trên thiết bị của bạn:\n\n"
            "- **Không lưu luồng camera**: Hệ thống không ghi hình, không lưu trữ video trực tiếp và "
            "cam kết không sử dụng công nghệ nhận diện khuôn mặt để định danh hay theo dõi người "
            "dùng.\n"
            "- **Chỉ lưu kết quả khi bạn xác nhận**: Nền tảng chỉ lưu trữ duy nhất 01 hình ảnh kết "
            "quả đã ướm bảng màu cùng báo cáo phân tích vào Hồ sơ cá nhân tại thời điểm bạn hoàn tất "
            "bài đánh giá và chọn lưu.\n"
            "- **Quyền riêng tư tuyệt đối**: Hình ảnh kết quả được cài đặt ở chế độ riêng tư, chỉ "
            "hiển thị với chính bạn và sẽ bị xóa hoàn toàn khỏi hệ thống khi bạn chủ động gỡ bỏ hoặc "
            "xóa tài khoản."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["policy"],
        "question": "TwistFit có sử dụng ảnh của tôi để nhận diện danh tính hay theo dõi không?",
        "answer_markdown": (
            "Tuyệt đối không. Hệ thống chỉ bóc tách màu sắc và cam kết không sử dụng công nghệ để "
            "nhận diện danh tính, theo dõi hay đối chiếu khuôn mặt người dùng."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["policy"],
        "question": "Tôi có thể chỉnh sửa/xóa bài đăng không, và bài đã xóa có khôi phục lại được không?",
        "answer_markdown": (
            "Có. Bạn có toàn quyền chỉnh sửa hoặc xóa bài viết bất cứ lúc nào. Lưu ý: sau khi xóa, "
            "bài viết sẽ bị xóa vĩnh viễn khỏi hệ thống ngay lập tức và không thể khôi phục lại được."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["policy"],
        "question": "Tôi có thể xem bài viết đã lưu từ Diễn đàn ở đâu?",
        "answer_markdown": (
            'Truy cập trang Diễn đàn và chọn mục "Đã lưu" trên thanh điều hướng để xem lại toàn bộ '
            "các bài viết bạn đã lưu từ cộng đồng."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["policy"],
        "question": "Tôi có sở hữu các nội dung/ảnh mình đăng lên TwistFit không?",
        "answer_markdown": (
            "Có. Bạn giữ toàn bộ quyền sở hữu trí tuệ đối với nội dung do mình tạo ra. TwistFit chỉ "
            "nhận quyền hiển thị nội dung đó trên hệ thống."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
    {
        "categories": ["policy"],
        "question": "Những hành vi/nội dung nào bị cấm đăng tải trên TwistFit?",
        "answer_markdown": (
            "Bạn không được phép:\n\n"
            "- Đăng ảnh khuôn mặt hoặc thông tin cá nhân của người khác khi chưa được cho phép.\n"
            "- Chia sẻ nội dung phản cảm, bạo lực, phân biệt đối xử hoặc vi phạm pháp luật.\n"
            "- Phát tán đường link chứa mã độc, trang web lừa đảo hoặc rác/spam."
        ),
        "highlight_icon": None,
        "highlight_text": None,
    },
]


def seed_demo_faq_items(db: Session) -> None:
    if db.query(FaqItem).count() > 0:
        return
    for item in DEMO_FAQ_ITEMS:
        db.add(FaqItem(**item))
    db.commit()
