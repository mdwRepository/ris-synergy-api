# -*- coding: utf-8 -*-
"""
This module contains tests for template filters.
"""

from datetime import datetime
import pytest
from flask import Flask
from app.template_filters import register_template_filters


@pytest.fixture
def app():
    """Fixture to create a Flask app and register template filters."""
    app = Flask(__name__)
    register_template_filters(app)
    return app


def test_isoformat_to_human_valid(app):
    """Test converting a valid ISO 8601 datetime string."""
    with app.app_context():
        input_value = "2024-11-22T14:30:00"
        expected_output = "November 22, 2024 14:30"
        result = app.jinja_env.filters["isoformat_to_human"](input_value)
        assert result == expected_output


def test_isoformat_to_human_with_timezone(app):
    """Test converting an ISO 8601 datetime string with UTC timezone."""
    with app.app_context():
        input_value = "2024-11-22T14:30:00Z"  # UTC timezone
        expected_output = "November 22, 2024 14:30"
        result = app.jinja_env.filters["isoformat_to_human"](input_value)
        assert result == expected_output


def test_isoformat_to_human_invalid(app):
    """Test handling of invalid ISO 8601 string."""
    with app.app_context():
        input_value = "invalid-datetime-string"
        result = app.jinja_env.filters["isoformat_to_human"](input_value)
        assert result == input_value  # Should return the original value


def test_isoformat_to_human_none(app):
    """Test handling of None value."""
    with app.app_context():
        input_value = None
        result = app.jinja_env.filters["isoformat_to_human"](input_value)
        assert result == ""  # Should return an empty string
