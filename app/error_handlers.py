# -*- coding: utf-8 -*-

from flask import jsonify


def register_error_handlers(app):
    """
    Register error handlers for the application
    """

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify(error="500 Error: Internal server error"), 500

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify(error="403 Error: Forbidden"), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify(error="404 Error: Page not found"), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify(error="405 Error: Method not allowed"), 405

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(error="400 Error: Bad request"), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify(error="401 Error: Unauthorized"), 401

    @app.errorhandler(429)
    def too_many_requests(error):
        return jsonify(error="429 Error: Too many requests"), 429

    @app.errorhandler(503)
    def service_unavailable(error):
        return jsonify(error="503 Error: Service unavailable"), 503
