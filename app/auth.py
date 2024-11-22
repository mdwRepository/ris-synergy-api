# -*- coding: utf-8 -*-
"""
Module: auth.py

This module handles authentication logic for the Flask application. It provides
a function to verify access tokens using Keycloak's introspection endpoint.

Functions:
- `verify_token(token)`: Verifies the validity of an access token by
  communicating with Keycloak's introspection endpoint. If the token is invalid
  or expired, an appropriate HTTP error is raised.

Dependencies:
- `requests`: Used to make HTTP requests to Keycloak.
- `flask`: Utilized for raising HTTP errors and accessing application
  configuration.

Keycloak Configuration:
The module relies on Flask's application configuration to retrieve Keycloak
settings:
- `KEYCLOAK_INTROSPECT_URI`: The URI of the Keycloak introspection endpoint.
- `OIDC_CLIENT_ID`: The client ID for the application in Keycloak.
- `OIDC_CREDENTIALS_SECRET`: The client secret for authentication.

Raises:
- `HTTP 500`: If there is an error connecting to the Keycloak server.
- `HTTP 401`: If the token is invalid or expired.
"""


import requests

from flask import abort, current_app


def verify_token(token):
    """
    Verify the access token with Keycloak's introspection endpoint.
    """
    # Get the Keycloak introspection endpoint and client credentials
    introspect_url = current_app.config["KEYCLOAK_INTROSPECT_URI"]
    client_id = current_app.config["OIDC_CLIENT_ID"]
    client_secret = current_app.config["OIDC_CREDENTIALS_SECRET"]

    # Prepare the introspection request to Keycloak
    response = requests.post(
        introspect_url,
        data={"token": token},
        auth=(client_id, client_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=5,
    )

    # Check if the request was successful otherwise raise an error
    if response.status_code != 200:
        abort(500, description="Error connecting to authentication server")

    # Parse the response from Keycloak
    token_data = response.json()
    # Check if the token is active
    if not token_data.get("active", False):
        abort(401, description="Invalid or expired token")

    return token_data
