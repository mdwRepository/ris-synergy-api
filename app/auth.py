# -*- coding: utf-8 -*-

import requests

from flask import abort, current_app


def verify_token(token):
    """Verify the access token with Keycloak's introspection endpoint."""
    introspect_url = current_app.config["KEYCLOAK_INTROSPECT_URI"]
    client_id = current_app.config["OIDC_CLIENT_ID"]
    client_secret = current_app.config["OIDC_CREDENTIALS_SECRET"]

    # Prepare the introspection request to Keycloak
    response = requests.post(
        introspect_url,
        data={"token": token},
        auth=(client_id, client_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code != 200:
        abort(500, description="Error connecting to authentication server")

    token_data = response.json()
    if not token_data.get("active", False):
        abort(401, description="Invalid or expired token")

    return token_data