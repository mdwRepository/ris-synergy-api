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
  - Configures security headers like `X-Frame-Options` and `Content-Security-Policy` to protect against clickjacking and other attacks.

Environment Variables:
- `SECRET_KEY`: The secret key for the Flask application.
- `LOG_LEVEL`: The logging level (e.g., DEBUG, INFO, WARNING, ERROR).
- `LOG_FOLDER`: The folder where log files are stored.
- `STATIC_URL_PATH`: The URL path for serving static files.
- `STATIC_FOLDER`: The folder containing static files.
- `SENTRY_DSN`: The DSN for Sentry integration (optional).
- `OIDC_CLIENT_ID`, `OIDC_CREDENTIALS_SECRET`, `KEYCLOAK_TOKEN_URI`, `KEYCLOAK_INTROSPECT_URI`: Keycloak configuration settings.
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
import json

# import secrets

from os import getenv
from dotenv import load_dotenv
from flask import Flask, g
from flasgger import Swagger

# from cryptography.fernet import Fernet

from app.extensions import cors
from .template_filters import register_template_filters
from .error_handlers import register_error_handlers

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


# check if .env file exists and required environment variables are set
if check_if_env_file_exists():
    load_dotenv(override=True)
if not check_if_required_env_variables_are_set():
    sys.exit("Error: required environment variables not set")


# Sentry utility function
def is_sentry_enabled():
    """
    Check if Sentry is enabled by verifying the presence of the SENTRY_DSN environment variable.
    """
    return bool(os.getenv("SENTRY_DSN"))


# Initialize Sentry if enabled
if is_sentry_enabled():
    import sentry_sdk

    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        traces_sample_rate=1.0,  # Capture 100% of transactions for performance monitoring
    )


def configure_keycloak_settings(app):
    """
    Configure Keycloak settings if the required environment variables are set.
    """
    oidc_client_id = os.getenv("OIDC_CLIENT_ID")
    if (
        oidc_client_id and oidc_client_id.strip()
    ):  # Check if OIDC_CLIENT_ID exists and is not empty
        app.config["OIDC_CLIENT_ID"] = oidc_client_id
        app.config["OIDC_CREDENTIALS_SECRET"] = os.getenv("OIDC_CREDENTIALS_SECRET")
        app.config["KEYCLOAK_TOKEN_URI"] = os.getenv("KEYCLOAK_TOKEN_URI")
        app.config["KEYCLOAK_INTROSPECT_URI"] = os.getenv("KEYCLOAK_INTROSPECT_URI")
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
    print("Error: ", e)
except Exception as e:
    print("Error: ", e)


def create_app():
    """
    Create a Flask app.
    """
    try:
        if static_url_path and static_folder:
            app = Flask(
                __name__, static_url_path=static_url_path, static_folder=static_folder
            )
        elif static_url_path or static_folder:
            sys.exit(
                "Please supply NEITHER or BOTH of STATIC_URL_PATH and STATIC_FOLDER"
            )
        else:
            app = Flask(__name__)

        print("creating app...")
        print(app)

        # Set the secret key to some random bytes. Keep this really secret!
        # app.secret_key = secrets.token_hex(
        #     16
        # )  # Generates a 32-character hexadecimal string (16 bytes)

        app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

        configure_logger(app)
        register_error_handlers(app)
        register_template_filters(app)
        register_blueprints(app)
        secure_app(app)

        # Configure Keycloak settings
        app.config["KEYCLOAK_ENABLED"] = configure_keycloak_settings(app)

        # Register Swagger (after blueprints)
        register_swagger(app)
        return app
    except Exception as e:
        print("Error: ", e)
        sys.exit("Error: creating app")


def configure_logger(app):
    """
    Configure loggers.
    """
    try:
        from .logging_setup import (
            setup_file_handler,
            setup_stream_handler,
            create_log_folder,
        )

        # Add the handlers to the app's logger
        create_log_folder()
        app.logger.addHandler(setup_file_handler())
        if setup_stream_handler() is not None:
            app.logger.addHandler(setup_stream_handler())
    except Exception as e:
        print("Error: ", e)
        sys.exit("Error: configuring logger")


def register_extensions(app):
    """
    Register extensions with the app.
    """
    cors.init_app(app)
    return None


def register_blueprints(app):
    """
    Register blueprints with the app.
    """
    try:
        # register the default blueprints required by the app
        from app.public.views import blueprint as public_blueprint

        print("registering default blueprints...")
        print("public blueprint")
        app.register_blueprint(public_blueprint)

        # load blueprints from the environment variable ENABLED_BLUEPRINTS
        enabled_blueprints = getenv("ENABLED_BLUEPRINTS")

        # register the blueprints
        if enabled_blueprints:
            print("Enabled blueprints: ", enabled_blueprints)
            for blueprint_name in enabled_blueprints.split(","):
                try:
                    blueprint = __import__(f"app.{blueprint_name}.views", fromlist=[""])
                    app.register_blueprint(blueprint.blueprint)
                    print(f"Registered blueprint: {blueprint_name}")
                except ImportError as e:
                    print(f"Failed to import or register blueprint: {e}")
                except Exception as e:
                    print("Error: ", e)
                    sys.exit("Error: registering blueprints")

            print("Available routes in the blueprints:")
            for rule in app.url_map.iter_rules():
                print(f"{rule.rule} -> {rule.endpoint}")

        return None
    except ImportError as e:
        print(f"Failed to import or register blueprint: {e}")
    except Exception as e:
        print("Error: ", e)
        sys.exit("Error: registering blueprints")


def register_swagger(app):
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
                    "rule_filter": lambda rule: True,  # include all routes
                    "model_filter": lambda tag: True,  # include all models
                }
            ],
        }

        # Initialize Swagger with the custom config
        swagger = Swagger(app, config=swagger_config)

        if swagger:
            print("Swagger UI registered")

            # Debugging: Log all registered routes
            print("Registered Routes:")
            for rule in app.url_map.iter_rules():
                print(f"{rule.endpoint}: {rule.rule}")

            # Log registered endpoints that are documented by Swagger
            print("Endpoints documented by Swagger:")
            for rule in app.url_map.iter_rules():
                # Check if the rule is for Swagger UI
                if "swagger" in rule.endpoint:
                    print(f"{rule.endpoint}: {rule.rule}")

        return None

    except Exception as e:
        print(f"Error: {e}")
        sys.exit("Error: registering Swagger UI")


def secure_app(app):
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
