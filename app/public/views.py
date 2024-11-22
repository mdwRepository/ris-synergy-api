# -*- coding: utf-8 -*-
"""
Module: views.py

This module defines the public-facing routes and views for the Flask application. 
It uses a Flask blueprint to modularize the application and provides endpoints 
for serving static files, rendering the main page, and a health check.

Blueprint:
- `blueprint`: The public blueprint for static file serving and index page rendering.

Routes:
- `/static/<path:filename>`: Serves static files from the configured static folder 
  with custom security headers.
- `/`: Renders the main index page with theme and Matomo analytics configuration, 
  as set by decorators.
- `/ping`: A health check endpoint for monitoring the application's status.

Decorators:
- `@set_theme`: Adds theme information to the request context.
- `@set_matomo_enabled`: Adds Matomo analytics configuration to the request context.

Environment Variables:
- `STATIC_URL_PATH`: The URL path used for serving static files.
- `STATIC_FOLDER`: The folder where static files are stored.

Error Handling:
- All routes include basic error handling that logs exceptions and returns a JSON 
  response with an error message and a 500 status code in case of failure.

Dependencies:
- Flask modules for routing, templates, and responses.
- Custom decorators from `app.decorators` for setting request-specific context.

Usage:
This module is registered as a blueprint in the application setup process. To 
register the blueprint:
    app.register_blueprint(blueprint)
"""


import logging
import os


from flask import (
    Blueprint,
    send_from_directory,
    render_template,
    request,
    jsonify,
)

from app.decorators import (
    set_theme,
    set_matomo_enabled,
)


static_url_path = os.getenv("STATIC_URL_PATH") or None
static_folder = os.getenv("STATIC_FOLDER") or None

logging.debug("static url path: ", static_url_path)
logging.debug("static folder: ", static_folder)

# create a blueprint
blueprint = Blueprint(
    "public", __name__, static_url_path=static_url_path, static_folder=static_folder
)


@blueprint.route("/static/<path:filename>")
def custom_static(filename):
    """
    Serve static files with custom headers
    """
    try:
        response = send_from_directory(static_folder, filename)
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response
    except Exception as e:
        logging.error(e)
        return jsonify({"error": "Internal server error"}), 500


@blueprint.route("/", methods=["GET", "POST"])
@set_theme
@set_matomo_enabled
def index_route():
    try:
        # Access the theme set by the set_theme decorator and matomo_enabled and login_enabled
        theme = request.theme
        matomo_enabled = request.matomo_enabled
        matomo_url = request.matomo_url
        matomo_site_id = request.matomo_site_id
        return render_template(
            "public/index.html",
            theme=theme,
            matomo_enabled=matomo_enabled,
            matomo_url=matomo_url,
            matomo_site_id=matomo_site_id,
        )
    except Exception as e:
        logging.error(e)
        return jsonify({"error": "Internal server error"}), 500


@blueprint.route("/ping", methods=["HEAD", "GET"])
def ping_route():
    """
    Health check endpoint.
    """
    return "OK"
