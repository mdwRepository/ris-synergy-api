# -*- coding: utf-8 -*-

import logging
import os
import sys
import time
import json

# import secrets

# from cryptography.fernet import Fernet
from dotenv import load_dotenv
from flask import Flask, g, Response
from flasgger import Swagger
from os import getenv

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
    else:
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
            logging.error(f"Error: {env_variable} not set")
            return False
    return True


# check if .env file exists and required environment variables are set
if check_if_env_file_exists():
    load_dotenv(override=True)
if not check_if_required_env_variables_are_set():
    sys.exit("Error: required environment variables not set")

# if sentry is enabled, initialize it
if os.getenv("SENTRY_DSN"):
    import sentry_sdk

    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
    )


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
                    "model_filter": lambda tag: True,   # include all models
                }
            ]
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
    g.request_start_time = time.time()
    g.request_time = lambda: f"{time.time() - g.request_start_time:.5f}s"


@app.after_request
def apply_clickjacking_protection(response):
    """
    Apply clickjacking protection to all responses
    """
    allowed_sources = os.getenv("ALLOWED_SOURCES")
    if allowed_sources:
        response.headers["X-Frame-Options"] = f"ALLOW-FROM  {allowed_sources}"
        response.headers["Content-Security-Policy"] = (
            f"frame-ancestors {allowed_sources}"
        )
    else:
        response.headers["X-Frame-Options"] = (
            "SAMEORIGIN"  # Or "DENY" if you don't want to allow framing even from the same origin
        )
        response.headers["Content-Security-Policy"] = "frame-ancestors 'self'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.after_request
def apply_hsts(response: Response) -> Response:
    # Enforce HTTPS-only communication for 1 year (in seconds)
    # `includeSubDomains` applies HSTS to all subdomains.
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
