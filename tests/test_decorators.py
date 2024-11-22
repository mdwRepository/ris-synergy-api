# -*- coding: utf-8 -*-
"""
Module for testing decorators in the Flask application.
"""

import pytest
from flask import Flask, request, jsonify
from app.decorators import (
    set_theme,
    set_matomo_enabled,
    caching,
    keycloak_protected,
    conditional_produces,
)


@pytest.fixture
def app_with_context():
    """Fixture to create a Flask app with a request context."""
    app = Flask(__name__)
    app.config["KEYCLOAK_ENABLED"] = True

    @app.route("/theme")
    @set_theme
    def theme_route():
        return jsonify(theme=request.theme, portal_name=request.portal_name)

    @app.route("/matomo")
    @set_matomo_enabled
    def matomo_route():
        return jsonify(
            matomo_enabled=request.matomo_enabled,
            matomo_url=request.matomo_url,
            matomo_site_id=request.matomo_site_id,
        )

    @app.route("/cache")
    @caching(3600)
    def cache_route():
        return "cached content"

    @app.route("/protected")
    @keycloak_protected
    def protected_route():
        return "protected content"

    @app.route("/content")
    @conditional_produces("application/json")
    def content_route():
        return jsonify(content="some content")

    with app.test_request_context():
        yield app


def test_set_theme(app_with_context, monkeypatch):
    """Test the set_theme decorator."""
    monkeypatch.setenv("THEME", "default")
    monkeypatch.setenv("PORTAL_NAME", "RIS Synergy")

    client = app_with_context.test_client()
    response = client.get("/theme")
    data = response.get_json()
    assert data["theme"] == "default"
    assert data["portal_name"] == "RIS Synergy"


def test_set_matomo_enabled(app_with_context, monkeypatch):
    """Test the set_matomo_enabled decorator."""
    monkeypatch.setenv("MATOMO_ENABLED", "true")
    monkeypatch.setenv("MATOMO_URL", "")
    monkeypatch.setenv("MATOMO_SITE_ID", "")

    client = app_with_context.test_client()
    response = client.get("/matomo")
    data = response.get_json()
    assert data["matomo_enabled"] == "true"
    assert data["matomo_url"] == ""
    assert data["matomo_site_id"] == ""


def test_caching(app_with_context):
    """Test the caching decorator."""
    client = app_with_context.test_client()
    response = client.get("/cache")
    assert response.headers["Cache-Control"] == "max-age=3600"


def test_conditional_produces(app_with_context):
    """Test the conditional_produces decorator."""
    client = app_with_context.test_client()
    response = client.get("/content", headers={"Accept": "application/json"})
    assert response.status_code == 200
    assert response.json == {"content": "some content"}
