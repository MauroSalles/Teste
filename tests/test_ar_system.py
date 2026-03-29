"""Tests for the AR experience system."""
import pytest
from unittest.mock import MagicMock

from backend.ar.ar_system import ARExperienceSystem


class TestARExperienceSystem:
    def setup_method(self):
        self.ar = ARExperienceSystem()

    def test_create_ar_experience_success(self):
        result = self.ar.create_ar_experience(1, ["granola", "banana"])
        assert result["success"] is True
        assert result["ar_ready"] is True
        model = result["model"]
        assert model["flavor_id"] == 1
        assert len(model["toppings"]) == 2
        assert "animations" in model
        assert "interactions" in model

    def test_create_ar_experience_no_toppings(self):
        result = self.ar.create_ar_experience(2, [])
        assert result["success"] is True
        assert result["model"]["toppings"] == []

    def test_ar_try_on_multiple_flavors(self):
        flavors = [
            {"id": 1, "name": "Chocolate", "default_toppings": ["granola"]},
            {"id": 2, "name": "Morango", "default_toppings": []},
        ]
        result = self.ar.ar_try_on_multiple_flavors(1, flavors)
        assert result["success"] is True
        assert len(result["slideshow"]["flavors"]) == 2
        assert result["slideshow"]["auto_advance"] is True

    def test_render_ar_on_hand(self):
        frame = MagicMock()
        model = {"flavor_id": 1}
        hand_position = {"x": 0.5, "y": 0.5, "z": 0.0}
        result = self.ar.render_ar_on_hand(frame, model, hand_position)
        assert result["rendered"] is True

    def test_capture_ar_screenshot(self):
        frame = MagicMock()
        model = {"flavor_id": 3}
        result = self.ar.capture_ar_screenshot(frame, model)
        assert result["success"] is True
        assert "image_path" in result
        assert "share_links" in result
        assert "instagram" in result["share_links"]
        assert "whatsapp" in result["share_links"]
