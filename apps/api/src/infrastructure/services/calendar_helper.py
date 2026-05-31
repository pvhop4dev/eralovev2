"""Calendar Helper.

Provides lunar calendar conversion, open-meteo weather requests,
and date-seeded daily horoscope and feng shui recommendations.
"""

from datetime import date

import httpx

# Supported LNY reference data
LUNAR_DATA = {
    2025: {
        "lny": date(2025, 1, 29),
        "months": [30, 29, 30, 29, 29, 30, 29, 30, 29, 30, 30, 29, 30],
        "names": ["1", "2", "3", "4", "5", "6", "6 nhuận", "7", "8", "9", "10", "11", "12"],
    },
    2026: {
        "lny": date(2026, 2, 17),
        "months": [30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29],
        "names": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
    },
    2027: {
        "lny": date(2027, 2, 6),
        "months": [30, 29, 30, 29, 29, 30, 29, 30, 29, 30, 30, 29, 30],
        "names": ["1", "2", "2 nhuận", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
    },
}

THIEN_CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
DIA_CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

HOROSCOPE_PREDICTIONS = [
    "Hôm nay là ngày tuyệt vời để chia sẻ những tâm tư thầm kín với đối phương. Sự lắng nghe sẽ kéo hai bạn lại gần nhau hơn.",
    "Một món quà nhỏ bất ngờ hoặc tin nhắn ngọt ngào vào giữa ngày sẽ làm hâm nóng tình cảm của hai bạn.",
    "Đừng ngần ngại bày tỏ tình cảm của mình. Đối phương đang rất mong chờ những lời khích lệ từ bạn đấy.",
    "Hôm nay hai bạn có thể gặp một chút bất đồng nhỏ, nhưng sự nhường nhịn và thấu hiểu sẽ giúp mọi chuyện êm đẹp.",
    "Một buổi hẹn hò lãng mạn tại một địa điểm mới lạ sẽ đem đến những cảm xúc mới mẻ cho tình yêu của hai bạn.",
    "Sự tin tưởng là chìa khóa cho ngày hôm nay. Hãy để đối phương có không gian riêng và ủng hộ những quyết định của họ.",
    "Hãy cùng nhau lên kế hoạch cho một chuyến đi chơi xa sắp tới. Việc cùng chuẩn bị sẽ tạo ra nhiều kỷ niệm vui vẻ.",
    "Hôm nay, thần tình yêu đang mỉm cười với bạn. Mọi cử chỉ quan tâm nhỏ bé đều được đối phương trân trọng và đáp lại.",
    "Dành thời gian để cùng nấu một bữa ăn ấm áp tại nhà sẽ là cách tuyệt vời nhất để gắn kết tình cảm hôm nay.",
    "Hãy lắng nghe trực giác của mình. Một cái ôm ấm áp lúc gặp mặt sẽ thay cho mọi lời nói hoa mỹ.",
]

FENG_SHUI_DIRECTIONS = ["Đông Nam", "Tây Bắc", "Chính Nam", "Chính Đông", "Tây Nam"]
FENG_SHUI_COLORS = ["Hồng cánh sen", "Tím oải hương", "Trắng sữa", "Xanh mint", "Vàng nhạt"]
FENG_SHUI_GOOD = [
    "Cùng dạo phố, chụp ảnh đôi, bày tỏ tình cảm.",
    "Nấu ăn chung, dọn dẹp không gian kỷ niệm.",
    "Lên kế hoạch du lịch, mua quà tặng bất ngờ.",
    "Chia sẻ kỷ niệm cũ, trò chuyện sâu sắc.",
    "Xem phim cùng nhau, thưởng thức trà chiều.",
]
FENG_SHUI_BAD = [
    "Tránh cãi vã về chuyện tiền bạc hoặc việc nhỏ nhặt.",
    "Tránh bàn luận các chủ đề nhạy cảm dễ gây bất đồng.",
    "Hạn chế trễ hẹn hoặc hủy hẹn vào phút chót.",
    "Tránh để những hiểu lầm kéo dài qua đêm.",
]


def get_lunar_date(d: date) -> str:
    """Calculate the Vietnamese lunar date with Can Chi naming."""
    # Day Can Chi (2026-05-31 is Mậu Thân)
    ref_d = date(2026, 5, 31)
    day_diff = (d - ref_d).days
    can_idx = (4 + day_diff) % 10
    chi_idx = (8 + day_diff) % 12
    day_can_chi = f"{THIEN_CAN[can_idx]} {DIA_CHI[chi_idx]}"

    if d.year in LUNAR_DATA:
        data = LUNAR_DATA[d.year]
        lny = data["lny"]
        if d >= lny:
            offset = (d - lny).days
            passed = 0
            for i, m_len in enumerate(data["months"]):
                if offset < passed + m_len:
                    lunar_day = offset - passed + 1
                    lunar_month = data["names"][i]
                    return f"Ngày {lunar_day} Tháng {lunar_month} âm lịch ({day_can_chi})"
                passed += m_len
        else:
            prev_year = d.year - 1
            if prev_year in LUNAR_DATA:
                data = LUNAR_DATA[prev_year]
                lny = data["lny"]
                offset = (d - lny).days
                passed = 0
                for i, m_len in enumerate(data["months"]):
                    if offset < passed + m_len:
                        lunar_day = offset - passed + 1
                        lunar_month = data["names"][i]
                        return f"Ngày {lunar_day} Tháng {lunar_month} âm lịch ({day_can_chi})"
                    passed += m_len

    return f"Ngày {d.day} Tháng {d.month}"


async def get_current_weather(
    latitude: float | None = None, longitude: float | None = None
) -> dict:
    """Fetch current weather from free Open-Meteo API or fallback."""
    lat = latitude if latitude is not None else 21.0285
    lng = longitude if longitude is not None else 105.8542

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current_weather=true"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=3.0)
            if response.status_code == 200:
                data = response.json()
                current = data.get("current_weather", {})
                temp = current.get("temperature", 28.0)
                windspeed = current.get("windspeed", 10.0)
                weathercode = current.get("weathercode", 0)

                weather_map = {
                    0: ("Nắng đẹp", "☀️"),
                    1: ("Ít mây", "🌤️"),
                    2: ("Nhiều mây", "⛅"),
                    3: ("U ám", "☁️"),
                    45: ("Sương mù", "🌫️"),
                    48: ("Sương mù", "🌫️"),
                    51: ("Mưa phùn nhẹ", "🌧️"),
                    53: ("Mưa phùn", "🌧️"),
                    55: ("Mưa phùn nhiều", "🌧️"),
                    61: ("Mưa nhẹ", "🌧️"),
                    63: ("Mưa vừa", "🌧️"),
                    65: ("Mưa to", "🌧️"),
                    80: ("Mưa rào nhẹ", "🌧️"),
                    81: ("Mưa rào vừa", "🌧️"),
                    82: ("Mưa rào to", "🌧️"),
                    95: ("Mưa giông", "⚡"),
                }
                desc, emoji = weather_map.get(weathercode, ("Nắng nhẹ", "☀️"))
                return {"temp": temp, "condition": desc, "emoji": emoji, "windspeed": windspeed}
    except Exception:
        pass

    return {"temp": 28.5, "condition": "Nắng ấm", "emoji": "☀️", "windspeed": 8.5}


def get_zodiac_love_horoscope(sign: str | None, d: date) -> str:
    """Generate date-seeded love horoscope predictions for a zodiac sign."""
    if not sign:
        return "Hãy điền đầy đủ ngày sinh của mình để xem tử vi đôi bạn nhé!"

    seed_str = f"{d.isoformat()}:{sign.lower()}"
    # Use built-in hash() with custom determinism based on seed
    # Since python hash() is randomized per process, let's use md5 for stable seeding
    import hashlib

    hash_val = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
    index = hash_val % len(HOROSCOPE_PREDICTIONS)
    return HOROSCOPE_PREDICTIONS[index]


def get_daily_feng_shui(d: date) -> dict:
    """Generate date-seeded feng shui recommendations."""
    import hashlib

    seed_str = d.isoformat()
    hash_val = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)

    dir_idx = hash_val % len(FENG_SHUI_DIRECTIONS)
    col_idx = (hash_val // 2) % len(FENG_SHUI_COLORS)
    good_idx = (hash_val // 3) % len(FENG_SHUI_GOOD)
    bad_idx = (hash_val // 4) % len(FENG_SHUI_BAD)

    return {
        "direction": FENG_SHUI_DIRECTIONS[dir_idx],
        "lucky_color": FENG_SHUI_COLORS[col_idx],
        "good_for": FENG_SHUI_GOOD[good_idx],
        "avoid": FENG_SHUI_BAD[bad_idx],
    }
