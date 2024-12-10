"""
Module for testing public views.
"""

from unittest.mock import patch
import os
import pytest
from flask import Flask
from app.public.views import blueprint


@pytest.fixture
def app_with_blueprint(monkeypatch):
    """Fixture to create a Flask app and register the public blueprint with an absolute template path."""
    # Use an absolute path to the templates directory
    template_path = os.path.abspath(os.path.join("app", "templates"))
    static_path = os.path.abspath(os.path.join("app", "static"))

    app = Flask(__name__, template_folder=template_path, static_folder=static_path)
    app.config["TESTING"] = True

    # Mock STATIC_FOLDER environment variable
    monkeypatch.setenv("STATIC_FOLDER", static_path)

    app.register_blueprint(blueprint)
    return app


def test_ping_route(app_with_blueprint):
    """Test the health check endpoint."""
    with app_with_blueprint.test_client() as client:
        response = client.get("/ping")
        assert response.status_code == 200
        assert response.data == b"OK"


def test_index_route_success(app_with_blueprint):
    """Test successful rendering of the index route."""
    with app_with_blueprint.app_context(), app_with_blueprint.test_client() as client:
        # Test the route directly without mocking render_template to ensure the template is rendered
        response = client.get("/")

        assert response.status_code == 200
        assert b"<h2>RIS Synergy API</h2>" in response.data
