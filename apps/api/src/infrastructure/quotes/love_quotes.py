"""Love Quotes — Vietnamese daily love quotes.

Provides a daily rotating quote, cached in Redis.
"""

import hashlib
from datetime import date

LOVE_QUOTES: list[dict[str, str]] = [
    {
        "text": "Yêu không phải là nhìn nhau, mà là cùng nhìn về một hướng.",
        "author": "Antoine de Saint-Exupéry",
    },
    {"text": "Nơi nào có tình yêu, nơi đó có sự sống.", "author": "Mahatma Gandhi"},
    {
        "text": "Tình yêu là khi hạnh phúc của người khác quan trọng hơn hạnh phúc của chính mình.",
        "author": "H. Jackson Brown Jr.",
    },
    {"text": "Em là giấc mơ đẹp nhất mà anh không muốn tỉnh dậy.", "author": "Eralove"},
    {"text": "Khoảng cách không là gì nếu trái tim luôn gần nhau.", "author": "Eralove"},
    {"text": "Mỗi ngày bên em là một ngày anh thêm yêu cuộc sống.", "author": "Eralove"},
    {"text": "Tình yêu không cần hoàn hảo, chỉ cần chân thành.", "author": "Eralove"},
    {
        "text": "Anh yêu em không phải vì em là ai, mà vì anh là ai khi ở bên em.",
        "author": "Roy Croft",
    },
    {
        "text": "Tình yêu bắt đầu từ một nụ cười, lớn lên bằng nụ hôn, và kết thúc bằng giọt nước mắt.",
        "author": "Khuyết danh",
    },
    {"text": "Yêu là cho đi mà không cần nhận lại.", "author": "Khuyết danh"},
    {"text": "Trái tim biết yêu là trái tim đẹp nhất.", "author": "Eralove"},
    {"text": "Em là lý do anh tin vào tình yêu.", "author": "Eralove"},
    {"text": "Cuộc sống ngắn ngủi, hãy yêu hết mình.", "author": "Eralove"},
    {"text": "Bên em, mọi ngày đều là Valentine.", "author": "Eralove"},
    {"text": "Yêu em là điều tuyệt vời nhất đã xảy ra với anh.", "author": "Eralove"},
    {"text": "Tình yêu không hoàn hảo, nhưng nó luôn xứng đáng.", "author": "Eralove"},
    {"text": "Anh muốn là người cuối cùng em nghĩ tới trước khi ngủ.", "author": "Eralove"},
    {"text": "Có em, anh không cần gì thêm nữa.", "author": "Eralove"},
    {"text": "Tình yêu chân chính không bao giờ lỗi thời.", "author": "Eralove"},
    {"text": "Mỗi khoảnh khắc bên em đều là kho báu.", "author": "Eralove"},
    {"text": "Tình yêu đích thực là khi bạn muốn chia sẻ mọi thứ.", "author": "Eralove"},
    {"text": "Em là nắng ấm trong ngày đông giá rét.", "author": "Eralove"},
    {"text": "Yêu nhau không phải là chiếm hữu, mà là đồng hành.", "author": "Eralove"},
    {"text": "Trái tim anh chỉ đập vì em.", "author": "Eralove"},
    {"text": "Tình yêu là cầu vồng sau cơn mưa.", "author": "Eralove"},
    {"text": "Một ngày không gặp em dài như cả thế kỷ.", "author": "Eralove"},
    {"text": "Bên em, anh tìm thấy ý nghĩa cuộc sống.", "author": "Eralove"},
    {"text": "Yêu em nhiều hơn hôm qua, ít hơn ngày mai.", "author": "Eralove"},
    {"text": "Em là ngôi sao sáng nhất trong bầu trời của anh.", "author": "Eralove"},
    {"text": "Tình yêu đích thực không bao giờ phai.", "author": "William Shakespeare"},
    {"text": "Hãy yêu như chưa bao giờ bị tổn thương.", "author": "Satchel Paige"},
    {"text": "Trong mắt anh, em là cả thế giới.", "author": "Eralove"},
    {"text": "Yêu em là hành trình đẹp nhất đời anh.", "author": "Eralove"},
    {"text": "Nắm tay em đi qua mọi giông bão.", "author": "Eralove"},
    {"text": "Tình yêu là ngọn lửa ấm áp trong đêm đông.", "author": "Eralove"},
    {"text": "Anh không cần cả thế giới, anh chỉ cần em.", "author": "Eralove"},
    {"text": "Tình yêu đẹp nhất là khi ta cùng nhau già đi.", "author": "Eralove"},
    {"text": "Em là trang đẹp nhất trong cuốn sách cuộc đời anh.", "author": "Eralove"},
    {"text": "Mỗi nhịp tim đều gọi tên em.", "author": "Eralove"},
    {"text": "Yêu em, anh học được cách trở thành phiên bản tốt nhất.", "author": "Eralove"},
    {"text": "Hôm nay, ngày mai và mãi mãi — anh yêu em.", "author": "Eralove"},
    {"text": "Tình yêu là khi im lặng cũng đủ hiểu nhau.", "author": "Eralove"},
    {"text": "Bên em, thời gian trôi qua thật nhẹ nhàng.", "author": "Eralove"},
    {"text": "Em là giấc mơ mà anh không muốn tỉnh.", "author": "Eralove"},
    {"text": "Yêu thương là ngôn ngữ đẹp nhất thế giới.", "author": "Eralove"},
    {"text": "Trái tim em là nơi anh muốn gọi là nhà.", "author": "Eralove"},
    {"text": "Mỗi nụ cười của em là một ngày nắng.", "author": "Eralove"},
    {"text": "Cùng nhau, chúng ta có thể vượt qua mọi thứ.", "author": "Eralove"},
    {"text": "Tình yêu không đếm ngày, tình yêu làm mỗi ngày đều đáng nhớ.", "author": "Eralove"},
    {"text": "Em là cả vũ trụ trong đôi mắt anh.", "author": "Eralove"},
]


def get_daily_quote(couple_id: str | None = None) -> dict[str, str]:
    """Get the daily love quote.

    Picks a quote based on the day of the year for consistent daily rotation.
    If couple_id is provided, uses it to personalize the rotation.

    Returns:
        Dict with "text" and "author" keys.
    """
    day_of_year = date.today().timetuple().tm_yday
    seed = f"{day_of_year}"
    if couple_id:
        seed = f"{day_of_year}:{couple_id}"

    # Use hash for consistent but varied selection
    hash_val = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    index = hash_val % len(LOVE_QUOTES)
    return LOVE_QUOTES[index]
