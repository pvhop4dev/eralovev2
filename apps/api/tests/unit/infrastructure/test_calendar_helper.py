"""Tests for Calendar Helper module."""

from datetime import date
from unittest.mock import AsyncMock, patch

import pytest

from infrastructure.services.calendar_helper import (
    get_current_weather,
    get_daily_feng_shui,
    get_lunar_date,
    get_zodiac_love_horoscope,
)


class TestCalendarHelper:
    """Test suite for Calendar Header Widget helper functions."""

    def test_get_lunar_date_specific(self):
        # 2026-05-31 is Mậu Thân and the 15th of the 4th lunar month
        d = date(2026, 5, 31)
        lunar_str = get_lunar_date(d)
        assert "Ngày 15" in lunar_str
        assert "Tháng 4" in lunar_str
        assert "Mậu Thân" in lunar_str

    def test_get_lunar_date_fallback(self):
        # Out of bounds year (e.g. 2030) should return a formatted string
        d = date(2030, 5, 1)
        lunar_str = get_lunar_date(d)
        assert "Ngày 1 Tháng 5" in lunar_str

    @pytest.mark.asyncio
    async def test_get_current_weather_success(self):
        # Mock successful open-meteo response
        from unittest.mock import MagicMock

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "current_weather": {
                "temperature": 25.5,
                "windspeed": 12.0,
                "weathercode": 0,  # Clear sky
            }
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.__aenter__.return_value = mock_client
            mock_client.get = AsyncMock(return_value=mock_response)
            weather = await get_current_weather(21.0285, 105.8542)

        assert weather["temp"] == 25.5
        assert weather["condition"] == "Nắng đẹp"
        assert weather["emoji"] == "☀️"
        assert weather["windspeed"] == 12.0

    @pytest.mark.asyncio
    async def test_get_current_weather_failure_fallback(self):
        # Mock weather API failure
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = mock_client_class.return_value
            mock_client.__aenter__.return_value = mock_client
            mock_client.get = AsyncMock(side_effect=Exception("Connection error"))
            weather = await get_current_weather(21.0285, 105.8542)

        # Should return fallback defaults
        assert weather["temp"] == 28.5
        assert weather["condition"] == "Nắng ấm"
        assert weather["emoji"] == "☀️"

    def test_get_zodiac_love_horoscope_consistency(self):
        sign = "Leo"
        d = date(2026, 5, 31)
        h1 = get_zodiac_love_horoscope(sign, d)
        h2 = get_zodiac_love_horoscope(sign, d)

        # Readings should be non-empty and deterministic on the same day
        assert len(h1) > 0
        assert h1 == h2

        # Readings should differ on a different day or sign
        h3 = get_zodiac_love_horoscope(sign, date(2026, 6, 1))
        h4 = get_zodiac_love_horoscope("Aries", d)
        assert h1 != h3 or h1 != h4  # Either date or sign should change value

    def test_get_daily_feng_shui_structure(self):
        d = date(2026, 5, 31)
        fs = get_daily_feng_shui(d)

        assert "direction" in fs
        assert "lucky_color" in fs
        assert "good_for" in fs
        assert "avoid" in fs
        assert len(fs["direction"]) > 0
        assert len(fs["lucky_color"]) > 0
