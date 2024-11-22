# -*- coding: utf-8 -*-
"""
Module: error_handlers.py

This module defines and registers custom error handlers for the Flask application.
These error handlers ensure consistent JSON-formatted error responses across the
application for common HTTP error codes.

Functions:
- `register_error_handlers(app)`: Registers error handlers for various HTTP
  status codes with the provided Flask application instance.

Error Handlers:
- `500`: Internal Server Error
- `403`: Forbidden
- `404`: Page Not Found
- `405`: Method Not Allowed
- `400`: Bad Request
- `401`: Unauthorized
- `429`: Too Many Requests
- `503`: Service Unavailable

Usage:
Call `register_error_handlers(app)` during the Flask application setup process
to enable these handlers.

Dependencies:
- `flask`: Used for defining error handlers and generating JSON responses.

Each error handler returns a JSON response with a standardized format:
{
    "error": "<Error Code and Description>"
}
"""

from flask import jsonify


def register_error_handlers(app):
    """
    Register error handlers for the application
    """

    @app.errorhandler(500)
    def internal_server_error(_):
        return jsonify(error="500 Error: Internal server error"), 500

    @app.errorhandler(403)
    def forbidden(_):
        return jsonify(error="403 Error: Forbidden"), 403

    @app.errorhandler(404)
    def not_found(_):
        return jsonify(error="404 Error: Page not found"), 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify(error="405 Error: Method not allowed"), 405

    @app.errorhandler(400)
    def bad_request(_):
        return jsonify(error="400 Error: Bad request"), 400

    @app.errorhandler(401)
    def unauthorized(_):
        return jsonify(error="401 Error: Unauthorized"), 401

    @app.errorhandler(429)
    def too_many_requests(_):
        return jsonify(error="429 Error: Too many requests"), 429

    @app.errorhandler(503)
    def service_unavailable(_):
        return jsonify(error="503 Error: Service unavailable"), 503
