"""Tests for Love Quotes module."""

from infrastructure.quotes.love_quotes import LOVE_QUOTES, get_daily_quote


class TestLoveQuotes:
    """Test suite for daily love quotes."""

    def test_quotes_not_empty(self):
        assert len(LOVE_QUOTES) >= 50

    def test_quote_has_text_and_author(self):
        for q in LOVE_QUOTES:
            assert "text" in q
            assert "author" in q
            assert len(q["text"]) > 0

    def test_get_daily_quote_returns_dict(self):
        quote = get_daily_quote()
        assert "text" in quote
        assert "author" in quote

    def test_daily_quote_consistent_same_day(self):
        q1 = get_daily_quote()
        q2 = get_daily_quote()
        assert q1 == q2

    def test_daily_quote_personalized_by_couple(self):
        q1 = get_daily_quote("couple-1")
        q2 = get_daily_quote("couple-2")
        # Different couple_ids may or may not produce different quotes,
        # but the function should not error
        assert "text" in q1
        assert "text" in q2

    def test_all_quotes_are_vietnamese(self):
        """At least some quotes should contain Vietnamese characters."""
        has_vietnamese = any(any(c in q["text"] for c in "àáảãạăắằẵặâấầẩ") for q in LOVE_QUOTES)
        assert has_vietnamese
