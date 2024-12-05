# -*- coding: utf-8 -*-
"""
Module for testing environment variable setup and checks.
"""

import logging
import os
import time
from unittest.mock import patch, MagicMock
import pytest
from flask import Flask, g, jsonify
from app import (
    check_if_env_file_exists,
    check_if_required_env_variables_are_set,
    create_app,
    configure_keycloak_settings,
    configure_logger,
    register_blueprints,
    register_extensions,
    validate_app_env,
    apply_csp,
    apply_clickjacking_protection,
)


@pytest.fixture
def flask_app():
    """Fixture to provide a Flask app instance."""
    return Flask(__name__)


@pytest.fixture
def test_flask_app():
    """
    Create and configure a Flask app for testing.
    """
    app = Flask(__name__)

    @app.route("/test", methods=["GET"])
    def test_route():
        return jsonify({"message": "Hello, world!"})

    # Include the actual before_request and after_request handlers
    @app.before_request
    def before_request():
        g.request_start_time = time.time()
        g.request_time = lambda: f"{time.time() - g.request_start_time:.5f}s"

    return app


@pytest.fixture
def app_with_clickjacking_protection(monkeypatch):
    """Fixture to create a Flask app with the after_request clickjacking protection applied."""
    app = Flask(__name__)
    app.config["TESTING"] = True

    @app.route("/test")
    def test_route():
        return jsonify({"message": "Test response"})

    # Register the actual apply_clickjacking_protection function
    app.after_request(apply_clickjacking_protection)

    return app


@pytest.fixture
def app_with_csp():
    """Fixture to create a Flask app with the after_request CSP applied."""
    app = Flask(__name__)
    app.config["TESTING"] = True

    @app.route("/test")
    def test_route():
        return jsonify({"message": "Test response"})

    # Register the actual apply_csp function
    app.after_request(apply_csp)

    return app


@pytest.fixture
def app_with_clickjacking_protection(monkeypatch):
    """Fixture to create a Flask app with the after_request clickjacking protection applied."""
    app = Flask(__name__)
    app.config["TESTING"] = True

    @app.route("/test")
    def test_route():
        return jsonify({"message": "Test response"})

    # Register the actual apply_clickjacking_protection function
    app.after_request(apply_clickjacking_protection)

    return app


@pytest.fixture
def setup_env():
    """
    Fixture to set environment variables for testing.
    """
    os.environ["SECRET_KEY"] = "test_secret"
    os.environ["STATIC_URL_PATH"] = "/static"
    os.environ["STATIC_FOLDER"] = "static"
    os.environ["ENABLED_BLUEPRINTS"] = "public"
    yield
    os.environ.pop("SECRET_KEY", None)
    os.environ.pop("STATIC_URL_PATH", None)
    os.environ.pop("STATIC_FOLDER", None)
    os.environ.pop("ENABLED_BLUEPRINTS", None)


@pytest.fixture
def client(test_flask_app):
    """
    Provide a test client for the Flask app.
    """
    with test_flask_app.test_client() as client:
        yield client


def test_env_file_exists(tmp_path, monkeypatch):
    """
    Test if .env file existence is correctly identified.
    """
    dummy_env = tmp_path / ".env"
    dummy_env.write_text("SECRET_KEY=test_secret")

    # Change working directory to tmp_path so ".env" matches dummy_env
    monkeypatch.chdir(tmp_path)

    # Mock os.path.isfile to return True for the ".env" file in the current directory
    monkeypatch.setattr("os.path.isfile", lambda x: x == ".env")

    # Debugging: Print current working directory and files
    print("Current working directory:", os.getcwd())
    print("Files in current directory:", os.listdir(os.getcwd()))

    assert check_if_env_file_exists() is True


def test_env_file_missing(monkeypatch):
    """
    Test if .env file missing is correctly identified.
    """
    monkeypatch.setattr("os.path.isfile", lambda _: False)
    assert check_if_env_file_exists() is False


def test_required_env_variables_set():
    """
    Test if required environment variables are set.
    """
    assert check_if_required_env_variables_are_set()


def test_required_env_variables_missing(monkeypatch):
    """
    Test if missing environment variables are correctly flagged.
    """
    monkeypatch.setattr("os.getenv", lambda x: None if x == "SECRET_KEY" else "value")
    assert check_if_required_env_variables_are_set() is False


def test_sys_exit_on_missing_env(monkeypatch):
    """
    Test that the code exits with sys.exit when required environment variables are missing.
    """
    # Ensure check_if_env_file_exists returns True
    monkeypatch.setattr("app.check_if_env_file_exists", lambda: True)

    # Ensure check_if_required_env_variables_are_set returns False to trigger sys.exit
    monkeypatch.setattr("app.check_if_required_env_variables_are_set", lambda: False)

    # Test sys.exit behavior
    with pytest.raises(SystemExit) as exc_info:
        validate_app_env()

    assert exc_info.type == SystemExit
    assert str(exc_info.value) == "Error: required environment variables not set"


def test_no_sys_exit_when_env_is_set(monkeypatch):
    """
    Test that the code does not exit when environment variables are correctly set.
    """
    # Ensure check_if_env_file_exists returns True
    monkeypatch.setattr("app.check_if_env_file_exists", lambda: True)

    # Ensure check_if_required_env_variables_are_set returns True
    monkeypatch.setattr("app.check_if_required_env_variables_are_set", lambda: True)

    # Ensure no exception is raised
    try:
        validate_app_env()
    except SystemExit:
        pytest.fail("sys.exit was called unexpectedly")


def test_keycloak_settings_configured(monkeypatch, flask_app):
    """
    Test that Keycloak settings are configured when required environment variables are set.
    """
    monkeypatch.setenv("OIDC_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("OIDC_CREDENTIALS_SECRET", "test_secret")
    monkeypatch.setenv("KEYCLOAK_TOKEN_URI", "https://example.com/token")
    monkeypatch.setenv("KEYCLOAK_INTROSPECT_URI", "https://example.com/introspect")

    result = configure_keycloak_settings(flask_app)

    assert result is True
    assert flask_app.config["OIDC_CLIENT_ID"] == "test_client_id"
    assert flask_app.config["OIDC_CREDENTIALS_SECRET"] == "test_secret"
    assert flask_app.config["KEYCLOAK_TOKEN_URI"] == "https://example.com/token"
    assert (
        flask_app.config["KEYCLOAK_INTROSPECT_URI"] == "https://example.com/introspect"
    )


def test_keycloak_settings_not_configured_missing_client_id(monkeypatch, flask_app):
    """
    Test that Keycloak settings are not configured when OIDC_CLIENT_ID is missing.
    """
    # Only set partial environment variables
    monkeypatch.setenv("OIDC_CREDENTIALS_SECRET", "test_secret")
    monkeypatch.setenv("KEYCLOAK_TOKEN_URI", "https://example.com/token")
    monkeypatch.setenv("KEYCLOAK_INTROSPECT_URI", "https://example.com/introspect")

    result = configure_keycloak_settings(flask_app)

    assert result is False
    assert "OIDC_CLIENT_ID" not in flask_app.config


def test_keycloak_settings_not_configured_all_missing(monkeypatch, flask_app):
    """
    Test that Keycloak settings are not configured when all environment variables are missing.
    """
    # Unset all environment variables
    monkeypatch.delenv("OIDC_CLIENT_ID", raising=False)
    monkeypatch.delenv("OIDC_CREDENTIALS_SECRET", raising=False)
    monkeypatch.delenv("KEYCLOAK_TOKEN_URI", raising=False)
    monkeypatch.delenv("KEYCLOAK_INTROSPECT_URI", raising=False)

    result = configure_keycloak_settings(flask_app)

    assert result is False
    assert "OIDC_CLIENT_ID" not in flask_app.config


def test_static_paths_from_env(monkeypatch):
    """
    Test when STATIC_URL_PATH and STATIC_FOLDER are set in the environment.
    """
    monkeypatch.setenv("STATIC_URL_PATH", "/static")
    monkeypatch.setenv("STATIC_FOLDER", "static_dir")

    static_url_path = os.getenv("STATIC_URL_PATH") or None
    static_folder = os.getenv("STATIC_FOLDER") or None

    assert static_url_path == "/static"
    assert static_folder == "static_dir"


def test_configure_logger_success(monkeypatch, flask_app):
    """
    Test successful logger configuration.
    """
    # Mock logging-related functions
    monkeypatch.setattr("app.create_log_folder", lambda: None)
    mock_file_handler = MagicMock()
    mock_stream_handler = MagicMock()
    monkeypatch.setattr("app.setup_file_handler", lambda: mock_file_handler)
    monkeypatch.setattr("app.setup_stream_handler", lambda: mock_stream_handler)

    # Configure logger
    configure_logger(flask_app)

    # Assert handlers were added
    assert mock_file_handler in flask_app.logger.handlers
    assert mock_stream_handler in flask_app.logger.handlers


def test_configure_logger_os_error(monkeypatch, flask_app):
    """
    Test logger configuration with OSError.
    """
    # Mock create_log_folder to raise OSError
    monkeypatch.setattr(
        "app.create_log_folder",
        lambda: (_ for _ in ()).throw(OSError("Mocked OSError")),
    )

    # Mock print and sys.exit
    with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
        configure_logger(flask_app)

        # Assert print was called with the correct arguments
        mock_print.assert_called_once()  # Ensure `print` was called
        call_args = mock_print.call_args  # Retrieve the actual call arguments
        assert (
            call_args[0][0] == "OS Error: "
        )  # Check the first argument is the error message
        assert isinstance(
            call_args[0][1], OSError
        )  # Check the second argument is an OSError
        assert str(call_args[0][1]) == "Mocked OSError"  # Check the exception message

        # Assert sys.exit was called
        mock_exit.assert_called_once_with("Error: configuring logger")


def test_configure_logger_value_error(monkeypatch, flask_app):
    """
    Test logger configuration with ValueError.
    """

    # Mock setup_file_handler to raise ValueError
    def mock_setup_file_handler():
        raise ValueError("Mocked ValueError")

    monkeypatch.setattr("app.setup_file_handler", mock_setup_file_handler)

    # Mock create_log_folder to prevent any issues
    monkeypatch.setattr("app.create_log_folder", lambda: None)

    # Replace Flask app logger with a custom logger to avoid conflicts
    flask_app.logger = logging.getLogger("test_logger")

    # Mock print and sys.exit
    with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
        configure_logger(flask_app)

        # Retrieve actual print call arguments
        mock_print.assert_called_once()
        call_args = mock_print.call_args
        assert call_args[0][0] == "Value Error: "
        assert str(call_args[0][1]) == "Mocked ValueError"

        # Assert sys.exit was called with the appropriate error message
        mock_exit.assert_called_once_with("Error: configuring logger")


def test_register_extensions(flask_app):
    """
    Test registering extensions.
    """
    # Mock the CORS extension
    mock_cors = MagicMock()
    with patch("app.cors", mock_cors):
        register_extensions(flask_app)

        # Assert CORS init_app was called with the Flask app
        mock_cors.init_app.assert_called_once_with(flask_app)


def test_register_blueprints_default(monkeypatch, flask_app):
    """
    Test default blueprint registration.
    """
    # Mock public blueprint
    mock_blueprint = MagicMock()
    monkeypatch.setattr("app.public_blueprint", mock_blueprint)

    # Mock ENABLED_BLUEPRINTS to None
    monkeypatch.delenv("ENABLED_BLUEPRINTS", raising=False)

    # Mock the Flask app's `register_blueprint` method
    with patch.object(
        flask_app, "register_blueprint", wraps=flask_app.register_blueprint
    ) as mock_register:
        register_blueprints(flask_app)

        # Assert the public blueprint is registered
        mock_register.assert_called_once_with(mock_blueprint)


def test_register_blueprints_custom(monkeypatch, flask_app):
    """
    Test custom blueprint registration from ENABLED_BLUEPRINTS.
    """
    # Mock public blueprint
    mock_blueprint = MagicMock()
    monkeypatch.setattr("app.public_blueprint", mock_blueprint)

    # Mock the custom blueprint
    mock_custom_blueprint = MagicMock()

    # Mock the __import__ function to return a module with a `blueprint` attribute
    mock_module = MagicMock()
    mock_module.blueprint = mock_custom_blueprint
    with patch("builtins.__import__", return_value=mock_module):
        # Set ENABLED_BLUEPRINTS environment variable
        monkeypatch.setenv("ENABLED_BLUEPRINTS", "custom1,custom2")

        # Mock the Flask app's `register_blueprint` method
        with patch.object(
            flask_app, "register_blueprint", wraps=flask_app.register_blueprint
        ) as mock_register:
            register_blueprints(flask_app)

            # Assert the public blueprint is registered
            mock_register.assert_any_call(mock_blueprint)

            # Assert the custom blueprints are registered
            mock_register.assert_any_call(mock_custom_blueprint)


def test_register_blueprints_import_error(monkeypatch, flask_app):
    """
    Test blueprint registration with ImportError.
    """
    # Mock public blueprint
    mock_blueprint = MagicMock()
    monkeypatch.setattr("app.public_blueprint", mock_blueprint)

    # Set ENABLED_BLUEPRINTS
    monkeypatch.setenv("ENABLED_BLUEPRINTS", "invalid_blueprint")

    # Mock __import__ to raise ImportError
    with patch("builtins.__import__", side_effect=ImportError("Mocked ImportError")):
        # Mock print and sys.exit
        with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
            register_blueprints(flask_app)

            # Assert error message was printed
            mock_print.assert_any_call(
                "Failed to import or register blueprint: Mocked ImportError"
            )

            # Assert sys.exit was NOT called (the function continues execution for other blueprints)
            mock_exit.assert_not_called()


def test_register_blueprints_attribute_error(monkeypatch, flask_app):
    """
    Test blueprint registration with AttributeError.
    """
    # Mock public blueprint
    mock_blueprint = MagicMock()
    monkeypatch.setattr("app.public_blueprint", mock_blueprint)

    # Set ENABLED_BLUEPRINTS
    monkeypatch.setenv("ENABLED_BLUEPRINTS", "invalid_blueprint")

    # Mock __import__ to raise AttributeError
    with patch(
        "builtins.__import__", side_effect=AttributeError("Mocked AttributeError")
    ):
        # Mock print and sys.exit
        with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
            register_blueprints(flask_app)

            # Assert error message was printed
            mock_print.assert_any_call("AttributeError: Mocked AttributeError")

            # Assert sys.exit was called with the appropriate error message
            mock_exit.assert_called_once_with("Error: registering blueprints")


def test_register_blueprints_type_error(monkeypatch, flask_app):
    """
    Test blueprint registration with TypeError.
    """
    # Mock public blueprint
    mock_blueprint = MagicMock()
    monkeypatch.setattr("app.public_blueprint", mock_blueprint)

    # Set ENABLED_BLUEPRINTS
    monkeypatch.setenv("ENABLED_BLUEPRINTS", "invalid_blueprint")

    # Mock __import__ to raise TypeError
    with patch("builtins.__import__", side_effect=TypeError("Mocked TypeError")):
        # Mock print and sys.exit
        with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
            register_blueprints(flask_app)

            # Assert error message was printed
            mock_print.assert_any_call("TypeError: Mocked TypeError")

            # Assert sys.exit was called with the appropriate error message
            mock_exit.assert_called_once_with("Error: registering blueprints")


def test_create_app_with_static_paths(monkeypatch):
    """
    Test that the Flask app is created correctly when both STATIC_URL_PATH and STATIC_FOLDER are set.
    """
    # Set both environment variables
    monkeypatch.setenv("STATIC_URL_PATH", "/static")
    monkeypatch.setenv("STATIC_FOLDER", "static")

    # Mock other dependencies to focus on the static path behavior
    monkeypatch.setattr("app.configure_logger", lambda x: None)
    monkeypatch.setattr("app.register_error_handlers", lambda x: None)
    monkeypatch.setattr("app.register_template_filters", lambda x: None)
    monkeypatch.setattr("app.register_blueprints", lambda x: None)
    monkeypatch.setattr("app.secure_application", lambda: None)
    monkeypatch.setattr("app.configure_keycloak_settings", lambda x: None)
    monkeypatch.setattr("app.register_swagger", lambda x: None)

    # Test Flask app creation
    app = create_app()

    # Assert app was created with correct static path configuration
    assert app.static_url_path == "/static"
    assert app.static_folder == os.path.abspath(
        os.path.join("app", "static")
    )  # Match Flask's default behavior


def test_create_app_without_static_paths(monkeypatch):
    """
    Test that the Flask app is created correctly when both STATIC_URL_PATH and STATIC_FOLDER are not set.
    """
    # Unset both environment variables
    monkeypatch.delenv("STATIC_URL_PATH", raising=False)
    monkeypatch.delenv("STATIC_FOLDER", raising=False)

    # Mock other dependencies to focus on the static path behavior
    monkeypatch.setattr("app.configure_logger", lambda x: None)
    monkeypatch.setattr("app.register_error_handlers", lambda x: None)
    monkeypatch.setattr("app.register_template_filters", lambda x: None)
    monkeypatch.setattr("app.register_blueprints", lambda x: None)
    monkeypatch.setattr("app.secure_application", lambda: None)
    monkeypatch.setattr("app.configure_keycloak_settings", lambda x: None)
    monkeypatch.setattr("app.register_swagger", lambda x: None)

    # Test Flask app creation
    app = create_app()

    # Assert app was created with default static path configuration
    assert app.static_url_path == "/static"
    assert app.static_folder == os.path.abspath(
        os.path.join("app", "static")
    )  # Match Flask's default behavior


def test_before_request(client):
    """
    Test that the before_request function sets request_start_time and request_time.
    """
    with patch("time.time", return_value=12345.678):
        response = client.get("/test")
        assert response.status_code == 200
        assert g.request_start_time == 12345.678
        assert callable(g.request_time)
        assert g.request_time() == "0.00000s"


def test_apply_clickjacking_protection_default(client, monkeypatch):
    """
    Test the apply_clickjacking_protection function with default settings.
    """
    # Ensure ALLOWED_SOURCES is unset
    monkeypatch.delenv("ALLOWED_SOURCES", raising=False)

    response = client.get("/test")
    assert response.status_code == 200
    assert response.headers["X-Frame-Options"] == "SAMEORIGIN"
    assert response.headers["Content-Security-Policy"] == "frame-ancestors 'self'"
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_apply_clickjacking_protection_allowed_sources(client, monkeypatch):
    """
    Test the apply_clickjacking_protection function when ALLOWED_SOURCES is set.
    """
    monkeypatch.setenv("ALLOWED_SOURCES", "https://example.com")

    response = client.get("/test")
    assert response.status_code == 200
    assert response.headers["X-Frame-Options"] == "ALLOW-FROM  https://example.com"
    assert (
        response.headers["Content-Security-Policy"]
        == "frame-ancestors https://example.com"
    )
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_apply_csp(app_with_csp):
    """Test that the CSP header is applied to responses."""
    with app_with_csp.test_client() as client:
        response = client.get("/test")

        # Check if the response contains the Content-Security-Policy header
        assert response.status_code == 200
        assert "Content-Security-Policy" in response.headers

        # Validate the CSP header content
        csp = response.headers["Content-Security-Policy"]
        assert "default-src 'self'" in csp
        assert "script-src 'self'" in csp
        assert "style-src 'self'" in csp
        assert "img-src 'self'" in csp
        assert "font-src 'self'" in csp
        assert "frame-ancestors 'self'" in csp
        assert "object-src 'none'" in csp
        assert "connect-src 'self'" in csp
        assert "base-uri 'self'" in csp
        assert "form-action 'self'" in csp


def test_apply_clickjacking_protection_default(
    app_with_clickjacking_protection, monkeypatch
):
    """Test the default clickjacking protection headers."""
    # Override ALLOWED_SOURCES to ensure default behavior
    monkeypatch.delenv("ALLOWED_SOURCES", raising=False)

    with app_with_clickjacking_protection.test_client() as client:
        response = client.get("/test")

        # Check for default headers
        assert response.status_code == 200
        assert response.headers["X-Frame-Options"] == "SAMEORIGIN"
        assert response.headers["Content-Security-Policy"] == "frame-ancestors 'self'"
        assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_apply_clickjacking_protection_allowed_sources(
    app_with_clickjacking_protection, monkeypatch
):
    """Test clickjacking protection headers when ALLOWED_SOURCES is set."""
    allowed_sources = "https://example.com"
    monkeypatch.setenv("ALLOWED_SOURCES", allowed_sources)

    with app_with_clickjacking_protection.test_client() as client:
        response = client.get("/test")

        # Check headers for allowed sources
        assert response.status_code == 200
        assert response.headers["X-Frame-Options"] == f"ALLOW-FROM  {allowed_sources}"
        assert (
            response.headers["Content-Security-Policy"]
            == f"frame-ancestors {allowed_sources}"
        )
        assert response.headers["X-Content-Type-Options"] == "nosniff"
