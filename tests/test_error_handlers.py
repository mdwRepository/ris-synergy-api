# -*- coding: utf-8 -*-
"""
Module for testing error handlers.
"""

import pytest
from flask import Flask, jsonify, abort
from app.error_handlers import register_error_handlers


@pytest.fixture
def app_with_error_handlers():
    """Fixture to create a Flask app and register error handlers."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["PROPAGATE_EXCEPTIONS"] = (
        True  # Allow exceptions to propagate to error handlers
    )
    register_error_handlers(app)

    @app.route("/trigger_500")
    def trigger_500():
        abort(500)  # Trigger the 500 error handler

    @app.route("/trigger_403")
    def trigger_403():
        abort(403)  # Trigger the 403 error handler

    @app.route("/trigger_404")
    def trigger_404():
        abort(404)  # Trigger the 404 error handler

    @app.route("/trigger_405", methods=["POST"])
    def trigger_405():
        abort(405)  # Trigger the 405 error handler

    @app.route("/trigger_400")
    def trigger_400():
        abort(400)  # Trigger the 400 error handler

    @app.route("/trigger_401")
    def trigger_401():
        abort(401)  # Trigger the 401 error handler

    @app.route("/trigger_429")
    def trigger_429():
        abort(429)  # Trigger the 429 error handler

    @app.route("/trigger_503")
    def trigger_503():
        abort(503)  # Trigger the 503 error handler

    return app


def test_500_error(app_with_error_handlers):
    client = app_with_error_handlers.test_client()
    response = client.get("/trigger_500")
    assert response.status_code == 500
    assert response.json == {"error": "500 Error: Internal server error"}


def test_403_error(app_with_error_handlers):
    client = app_with_error_handlers.test_client()
    response = client.get("/trigger_403")
    assert response.status_code == 403
    assert response.json == {"error": "403 Error: Forbidden"}


def test_404_error(app_with_error_handlers):
    client = app_with_error_handlers.test_client()
    response = client.get("/trigger_404")
    assert response.status_code == 404
    assert response.json == {"error": "404 Error: Page not found"}


def test_405_error(app_with_error_handlers):
    client = app_with_error_handlers.test_client()
    response = client.get("/trigger_405")  # Using GET instead of POST
    assert response.status_code == 405
    assert response.json == {"error": "405 Error: Method not allowed"}


def test_400_error(app_with_error_handlers):
    client = app_with_error_handlers.test_client()
    response = client.get("/trigger_400")
    assert response.status_code == 400
    assert response.json == {"error": "400 Error: Bad request"}


def test_401_error(app_with_error_handlers):
    client = app_with_error_handlers.test_client()
    response = client.get("/trigger_401")
    assert response.status_code == 401
    assert response.json == {"error": "401 Error: Unauthorized"}


def test_429_error(app_with_error_handlers):
    client = app_with_error_handlers.test_client()
    response = client.get("/trigger_429")
    assert response.status_code == 429
    assert response.json == {"error": "429 Error: Too many requests"}


def test_503_error(app_with_error_handlers):
    client = app_with_error_handlers.test_client()
    response = client.get("/trigger_503")
    assert response.status_code == 503
    assert response.json == {"error": "503 Error: Service unavailable"}
