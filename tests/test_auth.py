# -*- coding: utf-8 -*-
"""
Module for testing the authentication functionality.
"""

from unittest.mock import patch, MagicMock
import requests
import pytest
from flask import Flask
from app.auth import verify_token


@pytest.fixture
def app_context():
    """
    Provide a Flask app context with Keycloak configurations for testing.
    """
    app = Flask(__name__)
    app.config["KEYCLOAK_INTROSPECT_URI"] = "https://keycloak.example.com/introspect"
    app.config["OIDC_CLIENT_ID"] = "test_client_id"
    app.config["OIDC_CREDENTIALS_SECRET"] = "test_client_secret"

    with app.app_context():
        yield app


@patch("app.auth.requests.post")
def test_verify_token_success(mock_post, app_context):
    """
    Test that verify_token successfully validates a token.
    """
    # Mock Keycloak's response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"active": True, "username": "test_user"}
    mock_post.return_value = mock_response

    # Call verify_token
    token = "test_token"
    token_data = verify_token(token)

    # Assertions
    mock_post.assert_called_once_with(
        app_context.config["KEYCLOAK_INTROSPECT_URI"],
        data={"token": token},
        auth=(
            app_context.config["OIDC_CLIENT_ID"],
            app_context.config["OIDC_CREDENTIALS_SECRET"],
        ),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=5,
    )
    assert token_data["active"] is True
    assert token_data["username"] == "test_user"


@patch("app.auth.requests.post")
def test_verify_token_invalid(mock_post, app_context):
    """
    Test that verify_token raises a 401 error for an invalid or expired token.
    """
    # Mock Keycloak's response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"active": False}
    mock_post.return_value = mock_response

    # Call verify_token and expect an HTTP 401 error
    with pytest.raises(Exception) as exc_info:
        verify_token("invalid_token")

    assert exc_info.value.code == 401
    assert "Invalid or expired token" in exc_info.value.description


@patch("app.auth.requests.post")
def test_verify_token_server_error(mock_post, app_context):
    """
    Test that verify_token raises a 500 error if the Keycloak server is unreachable.
    """
    # Mock Keycloak's response
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_post.return_value = mock_response

    # Call verify_token and expect an HTTP 500 error
    with pytest.raises(Exception) as exc_info:
        verify_token("test_token")

    assert exc_info.value.code == 500
    assert "Error connecting to authentication server" in exc_info.value.description


@patch("app.auth.requests.post")
def test_verify_token_request_exception(mock_post, app_context):
    """
    Test that verify_token raises a 500 error if the request fails.
    """
    # Simulate a request exception
    mock_post.side_effect = requests.RequestException

    # Call verify_token and expect an HTTP 500 error
    with pytest.raises(Exception) as exc_info:
        verify_token("test_token")

    assert exc_info.value.code == 500
    assert "Error connecting to authentication server" in exc_info.value.description
