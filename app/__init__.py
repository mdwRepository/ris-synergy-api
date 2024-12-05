# -*- coding: utf-8 -*-
"""
Module: __init__.py

This module initializes the Flask application for the project. It includes functions 
and configurations to set up the app's environment, logging, extensions, blueprints, 
Swagger UI, error handling, security features, and more.

Main Features:
- **Environment Management**:
  - Loads environment variables using `dotenv`.
  - Verifies the presence of required environment variables and the `.env` file.

- **Logging**:
  - Configures both file-based and console logging with rotation and custom formatting.

- **Extensions and Middleware**:
  - Registers extensions like CORS, error handlers, and template filters.
  - Configures before and after request hooks for request timing and clickjacking protection.

- **Blueprints**:
  - Dynamically registers blueprints specified in the `ENABLED_BLUEPRINTS` environment variable.
  - Logs registered routes and endpoints for debugging.

- **Keycloak Integration**:
  - Configures Keycloak authentication settings if the required environment variables are present.

- **Swagger UI**:
  - Integrates Swagger UI for API documentation.
  - Configures Swagger to document all application routes.

- **Security Enhancements**:
  - Configures security headers like `X-Frame-Options` and `Content-Security-Policy` 
    to protect against clickjacking and other attacks.

Environment Variables:
- `SECRET_KEY`: The secret key for the Flask application.
- `LOG_LEVEL`: The logging level (e.g., DEBUG, INFO, WARNING, ERROR).
- `LOG_FOLDER`: The folder where log files are stored.
- `STATIC_URL_PATH`: The URL path for serving static files.
- `STATIC_FOLDER`: The folder containing static files.
- `SENTRY_DSN`: The DSN for Sentry integration (optional).
- `OIDC_CLIENT_ID`, `OIDC_CREDENTIALS_SECRET`, `KEYCLOAK_TOKEN_URI`, `KEYCLOAK_INTROSPECT_URI`: 
   Keycloak configuration settings.
- `ENABLED_BLUEPRINTS`: Comma-separated list of blueprints to load.
- `ALLOWED_SOURCES`: Sources allowed in the `X-Frame-Options` header for clickjacking protection.

Usage:
This module is executed when the Flask app is initialized. Use `create_app()` to 
programmatically initialize and configure the Flask app.

Example:
    from app import create_app
    app = create_app()

Error Handling:
Gracefully exits with descriptive messages if required configurations are missing 
or initialization steps fail.

Notes:
- Ensure required environment variables are correctly set in the `.env` file.
- Review the security configurations to match your deployment environment.
"""


import logging
import os
import sys
import time

# import secrets

from os import getenv
from dotenv import load_dotenv
from flask import Flask, g, Response
from flasgger import Swagger

# from cryptography.fernet import Fernet

from app.extensions import cors
from app.public.views import blueprint as public_blueprint
from .template_filters import register_template_filters
from .error_handlers import register_error_handlers
from .logging_setup import (
    setup_file_handler,
    setup_stream_handler,
    create_log_folder,
)
from .utils import is_sentry_enabled

# key = Fernet.generate_key()
# cipher_suite = Fernet(key)


def check_if_env_file_exists():
    """
    Check if .env file exists.
    """
    if not os.path.isfile(".env"):
        print("Info: .env file not found")
        return False
    print("Info: .env file found")
    return True


def check_if_required_env_variables_are_set():
    """
    Check if required environment variables are set.
    """
    required_env_variables = [
        "SECRET_KEY",
    ]
    print("Info: checking if required environment variables are set")
    print(f"Info: required environment variables: {required_env_variables}")
    for env_variable in required_env_variables:
        if not os.getenv(env_variable):
            logging.error("Error: %s not set", env_variable)
            return False
    return True


def validate_app_env():
    """
    Initializes the application by checking the .env file and required environment variables.
    """
    if check_if_env_file_exists():
        load_dotenv(override=True)
    if not check_if_required_env_variables_are_set():
        sys.exit("Error: required environment variables not set")

# Initialize the application environment
validate_app_env()

# Initialize Sentry if enabled
if is_sentry_enabled():
    import sentry_sdk

    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        traces_sample_rate=1.0,  # Capture 100% of transactions for performance monitoring
    )


def configure_keycloak_settings(flask_app):
    """
    Configure Keycloak settings if the required environment variables are set.
    """
    oidc_client_id = os.getenv("OIDC_CLIENT_ID")
    if (
        oidc_client_id and oidc_client_id.strip()
    ):  # Check if OIDC_CLIENT_ID exists and is not empty
        flask_app.config["OIDC_CLIENT_ID"] = oidc_client_id
        flask_app.config["OIDC_CREDENTIALS_SECRET"] = os.getenv(
            "OIDC_CREDENTIALS_SECRET"
        )
        flask_app.config["KEYCLOAK_TOKEN_URI"] = os.getenv("KEYCLOAK_TOKEN_URI")
        flask_app.config["KEYCLOAK_INTROSPECT_URI"] = os.getenv(
            "KEYCLOAK_INTROSPECT_URI"
        )
        logging.info("Keycloak settings configured")
        return True
    logging.info("Keycloak settings not configured or empty")
    return False


# Initialize the app

print("initializing dspace service app...")

try:
    static_url_path = getenv("STATIC_URL_PATH") or None
    static_folder = getenv("STATIC_FOLDER") or None

    print("static url path: ", static_url_path)
    print("static folder: ", static_folder)

except ValueError as e:
    print("Value Error: ", e)
except OSError as e:
    print("OS Error: ", e)


def create_app():
    """
    Create a Flask app.
    """
    try:
        if static_url_path and static_folder:
            flask_app = Flask(
                __name__, static_url_path=static_url_path, static_folder=static_folder
            )
        elif static_url_path or static_folder:
            sys.exit(
                "Please supply NEITHER or BOTH of STATIC_URL_PATH and STATIC_FOLDER"
            )
        else:
            flask_app = Flask(__name__)

        print("creating app...")
        print(flask_app)

        # Set the secret key to some random bytes. Keep this really secret!
        # app.secret_key = secrets.token_hex(
        #     16
        # )  # Generates a 32-character hexadecimal string (16 bytes)

        flask_app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

        configure_logger(flask_app)
        register_error_handlers(flask_app)
        register_template_filters(flask_app)
        register_blueprints(flask_app)
        secure_application()

        # Configure Keycloak settings
        flask_app.config["KEYCLOAK_ENABLED"] = configure_keycloak_settings(flask_app)

        # Register Swagger (after blueprints)
        register_swagger(flask_app)
        return flask_app
    except (OSError, ValueError) as e:
        print("Error: ", e)
        sys.exit("Error: creating app")


def configure_logger(flask_app):
    """
    Configure loggers.
    """
    try:
        # Add the handlers to the app's logger
        create_log_folder()
        flask_app.logger.addHandler(setup_file_handler())
        if setup_stream_handler() is not None:
            flask_app.logger.addHandler(setup_stream_handler())
    except OSError as e:
        print("OS Error: ", e)
        sys.exit("Error: configuring logger")
    except ValueError as e:
        print("Value Error: ", e)
        sys.exit("Error: configuring logger")


def register_extensions(flask_app):
    """
    Register extensions with the app.
    """
    cors.init_app(flask_app)


def register_blueprints(flask_app) -> None:
    """
    Register blueprints with the app.
    """
    print("registering default blueprints...")
    print("public blueprint")
    flask_app.register_blueprint(public_blueprint)

    # load blueprints from the environment variable ENABLED_BLUEPRINTS
    enabled_blueprints = getenv("ENABLED_BLUEPRINTS")

    if not enabled_blueprints:
        print("No additional blueprints enabled.")
        return None

    # register the blueprints
    print("Enabled blueprints: ", enabled_blueprints)
    for blueprint_name in enabled_blueprints.split(","):
        try:
            blueprint = __import__(f"app.{blueprint_name}.views", fromlist=[""])
            flask_app.register_blueprint(blueprint.blueprint)
            print(f"Registered blueprint: {blueprint_name}")
        except ImportError as e:
            print(f"Failed to import or register blueprint: {e}")
        except AttributeError as e:
            print(f"AttributeError: {e}")
            sys.exit("Error: registering blueprints")
        except TypeError as e:
            print(f"TypeError: {e}")
            sys.exit("Error: registering blueprints")

    print("Available routes in the blueprints:")
    for rule in flask_app.url_map.iter_rules():
        print(f"{rule.rule} -> {rule.endpoint}")

    return None


def register_swagger(flask_app):
    """
    Register the Swagger UI and serve a custom /apispec_1.json.
    """
    try:
        # Define Swagger config to use the endpoint from the blueprint
        swagger_config = {
            "swagger": "2.0",
            "uiversion": 3,
            "headers": [],  # Ensure headers are defined as an empty list
            "specs": [
                {
                    "endpoint": "apispec",
                    # Use the blueprint's route for the OpenAPI spec
                    "route": "/ris-synergy/ris_synergy.json",
                    "rule_filter": lambda _: True,  # include all routes
                    "model_filter": lambda _: True,  # include all models
                }
            ],
        }

        # Initialize Swagger with the custom config
        swagger = Swagger(flask_app, config=swagger_config)

        if swagger:
            print("Swagger UI registered")

            # Debugging: Log all registered routes
            print("Registered Routes:")
            for rule in flask_app.url_map.iter_rules():
                print(f"{rule.endpoint}: {rule.rule}")

            # Log registered endpoints that are documented by Swagger
            print("Endpoints documented by Swagger:")
            for rule in flask_app.url_map.iter_rules():
                # Check if the rule is for Swagger UI
                if "swagger" in rule.endpoint:
                    print(f"{rule.endpoint}: {rule.rule}")

        return None

    except (ImportError, AttributeError, TypeError) as e:
        print(f"Error: {e}")
        sys.exit("Error: registering Swagger UI")


def secure_application():
    """
    Secure the app.
    """
    # app.config["SESSION_COOKIE_SECURE"] = True  # Only send cookies over HTTPS
    # app.config["SESSION_COOKIE_HTTPONLY"] = True  # Prevent JS access to session cookies
    return None


app = create_app()


# app-wide before_request and after_request decorators


@app.before_request
def before_request():
    """
    Set the start time of the request
    """
    # Set the start time of the request
    g.request_start_time = time.time()
    g.request_time = lambda: f"{time.time() - g.request_start_time:.5f}s"


@app.after_request
def apply_clickjacking_protection(response):
    """
    Apply clickjacking protection to all responses
    """
    # Set security headers to prevent clickjacking
    # env var ALLOWED_SOURCES can be set to allow framing from specific sources
    allowed_sources = os.getenv("ALLOWED_SOURCES")
    if allowed_sources:
        # Allow framing from specific sources
        # set response headers to allow framing from the specified sources
        response.headers["X-Frame-Options"] = f"ALLOW-FROM  {allowed_sources}"
        response.headers["Content-Security-Policy"] = (
            f"frame-ancestors {allowed_sources}"
        )
    else:
        response.headers["X-Frame-Options"] = (
            # "SAMEORIGIN" to allow framing from the same origin
            # Or "DENY" if you don't want to allow framing even from the same origin
            "SAMEORIGIN"
        )
        response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
    # Prevent MIME sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.after_request
def apply_csp(response: Response) -> Response:
    csp = (
        "default-src 'self'; "
        "script-src 'self' https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js; "
        "https://code.jquery.com/jquery-3.3.1.slim.min.js https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js; "
        "style-src 'self' https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css; "
        "img-src 'self'; "
        "font-src 'self' https://fonts.gstatic.com/s/oswald/v53/TK3_WkUHHAIjg75cFRf3bXL8LICs1_FvsUZiZQ.woff2; "
        "frame-ancestors 'self'; "
        "object-src 'none'; "
        "connect-src 'self'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    response.headers['Content-Security-Policy'] = csp
    return response
