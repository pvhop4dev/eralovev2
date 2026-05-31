"""Tests for Photo Domain Entity."""

from datetime import date
from uuid import uuid4

import pytest

from domain.entities.photo import Photo
from domain.exceptions import BusinessRuleError


class TestPhotoEntity:
    """Test suite for Photo entity."""

    def _make_photo(self, **overrides) -> Photo:
        defaults = {
            "couple_id": uuid4(),
            "uploaded_by": uuid4(),
            "s3_key": "events/my-photo.jpg",
            "original_url": "http://localhost:9000/eralove-media/events/my-photo.jpg",
        }
        defaults.update(overrides)
        return Photo(**defaults)

    def test_create_photo_success(self):
        photo = self._make_photo()
        assert photo.s3_key == "events/my-photo.jpg"
        assert photo.original_url == "http://localhost:9000/eralove-media/events/my-photo.jpg"
        assert photo.photo_date == date.today()
        assert photo.is_deleted is False

    def test_empty_s3_key_raises(self):
        with pytest.raises(BusinessRuleError, match="S3 key cannot be empty"):
            self._make_photo(s3_key="")

    def test_empty_url_raises(self):
        with pytest.raises(BusinessRuleError, match="Original URL cannot be empty"):
            self._make_photo(original_url="")

    def test_soft_delete_and_restore(self):
        photo = self._make_photo()
        photo.soft_delete()
        assert photo.is_deleted is True
        assert photo.deleted_at is not None

        # already deleted raises
        with pytest.raises(BusinessRuleError, match="already deleted"):
            photo.soft_delete()

        # restore
        photo.restore()
        assert photo.is_deleted is False
        assert photo.deleted_at is None

        # restore not deleted raises
        with pytest.raises(BusinessRuleError, match="not deleted"):
            photo.restore()

    def test_update_metadata(self):
        photo = self._make_photo()
        photo.update(caption="Love in Paris", photo_date=date(2025, 5, 20), location_name="Paris")
        assert photo.caption == "Love in Paris"
        assert photo.photo_date == date(2025, 5, 20)
        assert photo.location_name == "Paris"

    def test_to_dict(self):
        photo = self._make_photo(caption="Smile!")
        d = photo.to_dict()
        assert d["caption"] == "Smile!"
        assert d["s3_key"] == "events/my-photo.jpg"
        assert d["original_url"] == "http://localhost:9000/eralove-media/events/my-photo.jpg"
