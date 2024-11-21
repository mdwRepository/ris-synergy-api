# -*- coding: utf-8 -*-

##############################################################
# custom decorators for the Flask application                #
##############################################################

import logging
import os


from functools import wraps
from flask import request, make_response, current_app, abort, jsonify

from app import is_sentry_enabled
from app.auth import verify_token
from app.exceptions import TokenError

if is_sentry_enabled():
    import sentry_sdk


def set_theme(f):
    """
    Decorator to set theme for a route
    Also sets the portal name
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Adding theme to request context
        request.theme = os.getenv("THEME", "default")
        # Adding portal name to request context
        request.portal_name = os.getenv("PORTAL_NAME", "RIS Synergy")
        return f(*args, **kwargs)

    return decorated_function


def set_matomo_enabled(f):
    """
    Decorator to set matomo enabled for a route
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        request.matomo_enabled = os.getenv(
            "MATOMO_ENABLED", "true"
        )  # Adding matomo_enabled to request context
        request.matomo_url = os.getenv("MATOMO_URL", "")
        request.matomo_site_id = os.getenv("MATOMO_SITE_ID", "")
        return f(*args, **kwargs)

    return decorated_function


def caching(seconds):
    """
    Decorator to set cache control headers for a route
    @caching(3600)  # Cache for 1 hour
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            response.cache_control.max_age = seconds
            return response

        return decorated_function

    return decorator


def keycloak_protected(f):
    """
    A decorator to protect routes with Keycloak authentication.
    Verifies the token only if Keycloak is enabled in the app configuration.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_app.config.get("KEYCLOAK_ENABLED", False):
            try:
                # Token extraction and verification
                auth_header = request.headers.get("Authorization", None)
                if not auth_header or not auth_header.startswith("Bearer "):
                    # Skip logging this specific error to Sentry
                    abort(401, description="Authorization header missing or malformed")

                token = auth_header.split(" ")[1]
                verify_token(token)  # Verify the token with Keycloak
                
            except TokenError as e:
                # Log token-related errors
                if is_sentry_enabled():
                    # Skip logging this specific error to Sentry
                    if e.args[0] != "Authorization header missing or malformed":
                        sentry_sdk.capture_exception(e)
                logging.error("Token error: %s", e)
                response = {"error": e.args[0]}
                return jsonify(response), e.status_code
            
            except (KeyError, ValueError) as e:
                # Handle specific errors
                if is_sentry_enabled():
                    sentry_sdk.capture_exception(e)
                logging.error("Error during token verification: %s", e)
                response = {"error": str(e)}
                return jsonify(response), 400

        return f(*args, **kwargs)

    return decorated_function
