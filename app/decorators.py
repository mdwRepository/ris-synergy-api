# -*- coding: utf-8 -*-

##############################################################
# custom decorators for the Flask application                #
##############################################################

import os


from flask import request, make_response
from functools import wraps


def set_theme(f):
    """
    Decorator to set theme for a route
    Also sets the portal name
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        request.theme = os.getenv("THEME", "default")  # Adding theme to request context
        request.portal_name = os.getenv("PORTAL_NAME", "RIS Synergy") # Adding portal name to request context
        return f(*args, **kwargs)

    return decorated_function


def set_matomo_enabled(f):
    """
    Decorator to set matomo enabled for a route
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        request.matomo_enabled = os.getenv(
            "MAZOMO_ENABLED", "true"
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
