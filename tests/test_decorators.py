# -*- coding: utf-8 -*-
"""
Module for testing decorators in the Flask application.
"""

import pytest
from unittest.mock import patch
from flask import Flask, request, jsonify
from app.decorators import (
    set_theme,
    set_matomo_enabled,
    caching,
    keycloak_protected,
    conditional_produces,
)
from app.exceptions import TokenError


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


@pytest.fixture
def app_with_keycloak(monkeypatch):
    """Fixture to create a Flask app with Keycloak protection enabled."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["KEYCLOAK_ENABLED"] = True

    @app.route("/protected")
    @keycloak_protected
    def protected_route():
        return jsonify({"message": "Access granted"}), 200

    @app.errorhandler(401)
    def unauthorized_error(error):
        """
        Custom handler for 401 Unauthorized errors to ensure JSON responses.
        """
        return jsonify({"error": error.description}), 401

    return app


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


def test_keycloak_protected_valid_token(app_with_keycloak):
    """Test the decorator with a valid token."""
    with app_with_keycloak.test_client() as client:
        with patch("app.decorators.verify_token") as mock_verify_token:
            mock_verify_token.return_value = True
            headers = {"Authorization": "Bearer valid_token"}
            response = client.get("/protected", headers=headers)

            assert response.status_code == 200
            assert response.get_json() == {"message": "Access granted"}


def test_keycloak_protected_missing_header(app_with_keycloak):
    """Test the decorator with a missing Authorization header."""
    with app_with_keycloak.test_client() as client:
        response = client.get("/protected")

        assert response.status_code == 401
        assert (
            response.get_json()["error"] == "Authorization header missing or malformed"
        )


def test_keycloak_protected_malformed_header(app_with_keycloak):
    """Test the decorator with a malformed Authorization header."""
    with app_with_keycloak.test_client() as client:
        headers = {"Authorization": "InvalidHeader"}
        response = client.get("/protected", headers=headers)

        assert response.status_code == 401
        assert (
            response.get_json()["error"] == "Authorization header missing or malformed"
        )


def test_keycloak_protected_token_error(app_with_keycloak):
    """Test the decorator with a token error raised by verify_token."""
    with app_with_keycloak.test_client() as client:
        with patch("app.decorators.verify_token") as mock_verify_token:
            mock_verify_token.side_effect = TokenError("Invalid token", 401)
            headers = {"Authorization": "Bearer invalid_token"}
            response = client.get("/protected", headers=headers)

            assert response.status_code == 401
            assert response.get_json() == {"error": "Invalid token"}


def test_keycloak_protected_key_error(app_with_keycloak):
    """Test the decorator with a KeyError during token verification."""
    with app_with_keycloak.test_client() as client:
        with patch("app.decorators.verify_token") as mock_verify_token:
            mock_verify_token.side_effect = KeyError("Key missing")
            headers = {"Authorization": "Bearer valid_token"}
            response = client.get("/protected", headers=headers)

            assert response.status_code == 400
            assert response.get_json() == {"error": "Key missing"}


def test_keycloak_protected_keycloak_disabled():
    """Test the decorator when Keycloak is disabled."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["KEYCLOAK_ENABLED"] = False  # Keycloak is disabled

    @app.route("/protected")
    @keycloak_protected
    def protected_route():
        return jsonify({"message": "Access granted without Keycloak"})

    with app.test_client() as client:
        response = client.get("/protected")

        assert response.status_code == 200
        assert response.get_json() == {"message": "Access granted without Keycloak"}
