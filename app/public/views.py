# -*- coding: utf-8 -*-

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
