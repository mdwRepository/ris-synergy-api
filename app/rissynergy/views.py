# -*- coding: utf-8 -*-
"""
Module: views.py

This module defines routes for the `ris-synergy` blueprint, including endpoints for 
serving schemas, organizational unit data, and project data. It integrates with 
Swagger for API documentation, handles data retrieval, and ensures secure access 
via Keycloak-protected endpoints.

Blueprint:
- `blueprint`: The `ris-synergy` blueprint for managing RIS Synergy-related endpoints.

Environment Variables:
- `STATIC_URL_PATH`: The URL path for serving static files.
- `STATIC_FOLDER`: The folder containing static files.
- `SUPPORTED_API_VERSION`: The API version to use for schema resolution (default: "1.0").
- `OPEN_API_SERVER_URL`: The server URL to replace placeholders in schemas.
- Various paths for schema and JSON files are dynamically constructed based on the API version.

Key Functions:
- **Schema Handling**:
  - `get_ris_synergy_schema`: Serves the RIS Synergy JSON schema.
  - `get_info_schema`: Serves the JSON schema for the "info" endpoint.
  - `get_orgunit_schema`: Serves the JSON schema for organizational units.
  - `get_project_schema`: Serves the JSON schema for projects.

- **Data Retrieval**:
  - `get_info`: Fetches and serves data for the "info" endpoint.
  - `get_organigram`: Fetches and serves organizational hierarchy data.
  - `get_organigram_by_date`: Serves organizational hierarchy data for a specific date.
  - `get_orgunit`: Retrieves data for a specific organizational unit by ID.

- **Swagger Integration**:
  - `show_info_schema_apidocs`: Redirects to the Swagger UI for the "info" schema.
  - `show_orgunits_schema_apidocs`: Redirects to the Swagger UI for organizational units.
  - `show_projects_schema_apidocs`: Redirects to the Swagger UI for project schemas.

Decorators:
- `@keycloak_protected`: Secures endpoints requiring Keycloak authentication.
- `@produces`: Ensures responses adhere to specified content types.
- `@swag_from`: Integrates Flasgger for Swagger documentation.

Utilities:
- `is_valid_yaml`: Validates the structure of a YAML file.
- `get_latest_json_file`: Retrieves the most recent JSON file from the `JSON_DIR`.
- `replace_placeholder_in_file`: Replaces placeholders (e.g., `{{SERVER_URL}}`) in schema files.

Error Handling:
- Logs detailed errors for debugging.
- Returns appropriate HTTP error codes (`400`, `404`, `500`) for invalid input, missing data, or 
  server issues.

Usage:
This module is registered as a Flask blueprint and provides endpoints for managing 
schemas and organizational data, along with corresponding Swagger documentation.

Example Registration:
    app.register_blueprint(blueprint)
"""


import logging
import json
import os
import re
from pathlib import Path
from urllib.parse import urljoin
import yaml

from flask import (
    Blueprint,
    redirect,
    jsonify,
    abort,
    url_for,
)
from flasgger import swag_from
from werkzeug.utils import secure_filename

from app.decorators import keycloak_protected, conditional_produces, enabled_endpoint


static_url_path = os.getenv("STATIC_URL_PATH") or None
static_folder = os.getenv("STATIC_FOLDER") or None

logging.debug("static url path: %s", static_url_path)
logging.debug("static folder: %s", static_folder)

# Get the supported API version from the .env file
SUPPORTED_API_VERSION = os.getenv("SUPPORTED_API_VERSION", "1.0")

# Environment variable for server URL
OPEN_API_SERVER_URL = os.getenv("OPEN_API_SERVER_URL", "https://default-url.com")

# Path where the JSON files are stored
JSON_DIR = os.path.join(os.getcwd(), "app", "rissynergy", "organigram_data")

# Path to the OpenAPI schema JSON files

RIS_SYNERGY_SCHEMA_PATH = os.path.join(
    os.getcwd(), "app", "rissynergy", "jsonschemas", "ris-synergy.json"
)

ORGUNIT_SCHEMA_PATH = os.path.join(
    os.getcwd(),
    "app",
    "rissynergy",
    "jsonschemas",
    f"RIS-SYNERGY-org-unit_api-{SUPPORTED_API_VERSION}-resolved.json",
)
INFO_SCHEMA_PATH = os.path.join(
    os.getcwd(),
    "app",
    "rissynergy",
    "jsonschemas",
    f"RIS-SYNERGY-info-api-{SUPPORTED_API_VERSION}-resolved.json",
)
FUNDING_SCHEMA_PATH = os.path.join(
    os.getcwd(),
    "app",
    "rissynergy",
    "jsonschemas",
    f"funding-v.{SUPPORTED_API_VERSION}.json",
)
PROJECT_SCHEMA_PATH = os.path.join(
    os.getcwd(),
    "app",
    "rissynergy",
    "jsonschemas",
    f"RIS-SYNERGY-project-api-{SUPPORTED_API_VERSION}-resolved.json",
)
ORGUNIT_OPENAPI_SPEC_PATH = os.path.join(
    os.getcwd(),
    "app",
    "rissynergy",
    "openapi",
    f"RIS-SYNERGY-org-unit_api-{SUPPORTED_API_VERSION}-resolved.yaml",
)
INFO_OPENAPI_SPEC_PATH = os.path.join(
    os.getcwd(),
    "app",
    "rissynergy",
    "openapi",
    f"RIS-SYNERGY-info-api-{SUPPORTED_API_VERSION}-resolved.yaml",
)
FUNDING_OPENAPI_SPEC_PATH = os.path.join(
    os.getcwd(),
    "app",
    "rissynergy",
    "openapi",
    "funding.yaml",  # Assuming this doesn't depend on version
)
PROJECT_OPENAPI_SPEC_PATH = os.path.join(
    os.getcwd(),
    "app",
    "rissynergy",
    "openapi",
    f"RIS-SYNERGY-project-api-{SUPPORTED_API_VERSION}-resolved.yaml",
)
INFO_DATA_PATH = os.path.join(
    os.getcwd(), "app", "rissynergy", "info_data", f"info-{SUPPORTED_API_VERSION}.json"
)


# create a blueprint
blueprint = Blueprint(
    "ris-synergy",
    __name__,
    static_url_path=static_url_path,
    static_folder=static_folder,
)


def is_valid_yaml(file_path):
    """
    Check if a file contains valid YAML.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            yaml.safe_load(file)  # Try to parse the YAML file
        return True
    except yaml.YAMLError as e:
        logging.error("Invalid YAML in %s: %s", file_path, e)
        return False
    except FileNotFoundError as e:
        logging.error("Error reading %s: %s", file_path, e)
        return False


def get_latest_json_file():
    """
    Get the latest JSON file in the JSON_DIR directory.
    """
    try:
        files = [
            f
            for f in os.listdir(JSON_DIR)
            if f.startswith("organigram_") and f.endswith(".json")
        ]
        files.sort(reverse=True)
        if not files:
            raise FileNotFoundError("No JSON files found.")
        return files[0]
    except FileNotFoundError as e:
        logging.error("No JSON files found or directory missing: %s", e)
        return None
    except PermissionError as e:
        logging.error("Permission error accessing JSON_DIR: %s", e)
        return None
    except OSError as e:  # For other OS-related issues
        logging.error("OS error while accessing JSON_DIR: %s", e)
        return None


def replace_placeholder_in_file(
    file_path, placeholder="{{SERVER_URL}}", replacement=OPEN_API_SERVER_URL
):
    """
    Replace a placeholder in a JSON or YAML file with the given replacement.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace(placeholder, replacement)
        if file_path.endswith(".json"):
            return json.loads(content)
        if file_path.endswith(".yaml") or file_path.endswith(".yml"):
            return yaml.safe_load(content)
        raise ValueError("Unsupported file type")
    except (
        FileNotFoundError,
        json.JSONDecodeError,
        yaml.YAMLError,
        ValueError,
        OSError,
    ) as e:
        logging.error("Error processing file %s: %s", file_path, e)
        return None


@blueprint.route("/ris-synergy/ris_synergy.json", methods=["GET"])
@conditional_produces("application/json")
def get_ris_synergy_schema():
    """
    Get RIS Synergy JSON Schema
    This endpoint serves the JSON schema for the RIS Synergy endpoint.
    """
    try:
        schema = replace_placeholder_in_file(RIS_SYNERGY_SCHEMA_PATH)
        if schema is None:
            return jsonify({"error": "Internal server error"}), 500
        return jsonify(schema)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        logging.error("Error fetching JSON schema: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@blueprint.route("/ris-synergy/v1/info/schema", methods=["GET"])
@conditional_produces("application/json")
def get_info_schema():
    """
    Get Info JSON Schema
    Dynamically replaces placeholders with configured values.
    """
    try:
        schema = replace_placeholder_in_file(INFO_SCHEMA_PATH)
        if schema is None:
            return jsonify({"error": "Internal server error"}), 500
        return jsonify(schema)
    except (FileNotFoundError, ValueError, json.JSONDecodeError, yaml.YAMLError) as e:
        logging.error("Error fetching JSON schema: %s", e)
        return jsonify({"error": "Internal server error"}), 500


@blueprint.route("/ris-synergy/apidocs/info", methods=["GET"])
@swag_from(INFO_OPENAPI_SPEC_PATH)
def show_info_schema_apidocs():
    """
    Redirect to the Swagger UI with the search field pre-filled for info schema.
    """
    # Use url_for to dynamically build the path to the schema endpoint
    schema_url = urljoin(OPEN_API_SERVER_URL, url_for("ris-synergy.get_info_schema"))
    # Redirect to the Flasgger documentation UI with the schema URL as a query parameter
    return redirect(f"/apidocs?url={schema_url}")


@blueprint.route("/ris-synergy/v1/info", methods=["GET"], endpoint="info")
@swag_from(
    INFO_OPENAPI_SPEC_PATH,
    endpoint="ris-synergy.info",
    methods=["GET"],
)
@conditional_produces("application/json")
def get_info():
    """
    This endpoint serves the info data.
    """
    try:
        data = replace_placeholder_in_file(INFO_DATA_PATH)
        if data is None:
            return abort(500, description="Internal server error")
        return jsonify(data)
    except (FileNotFoundError, ValueError, json.JSONDecodeError, yaml.YAMLError) as e:
        logging.error("Error fetching info data: %s", e)
        return abort(500, description="Internal server error")


@blueprint.route("/ris-synergy/v1/orgUnits/schema", methods=["GET"])
@enabled_endpoint("orgunit")
@conditional_produces("application/json")
def get_orgunit_schema():
    """
    Get OrgUnit JSON Schema
    This endpoint serves the JSON schema for organizational units.
    """
    try:
        schema = replace_placeholder_in_file(ORGUNIT_SCHEMA_PATH)
        if schema is None:
            return abort(500, description="Internal server error")
        return jsonify(schema)
    except (FileNotFoundError, ValueError, json.JSONDecodeError, yaml.YAMLError) as e:
        logging.error("Error fetching JSON schema: %s", e)
        return abort(500, description="Internal server error")


@blueprint.route("/ris-synergy/apidocs/orgunit", methods=["GET"])
@enabled_endpoint("orgunit")
@swag_from(ORGUNIT_OPENAPI_SPEC_PATH)
def show_orgunits_schema_apidocs():
    """
    Redirect to the Swagger UI with the search field pre-filled for orgunit schema.
    """
    # Use url_for to dynamically build the path to the schema endpoint
    schema_url = urljoin(OPEN_API_SERVER_URL, url_for("ris-synergy.get_orgunit_schema"))
    # Redirect to the Flasgger documentation UI with the schema URL as a query parameter
    return redirect(f"/apidocs?url={schema_url}")


@blueprint.route(
    "/ris-synergy/v1/orgUnits/organigram", methods=["GET"], endpoint="organigram"
)
@swag_from(
    ORGUNIT_OPENAPI_SPEC_PATH,
    endpoint="ris-synergy.organigram",
    methods=["GET"],
)
@enabled_endpoint("orgunit")
@keycloak_protected
@conditional_produces("application/json")
def get_organigram():
    """
    Get Organigram Data
    This endpoint serves the organizational tree of the university.
    """
    try:
        # Replace placeholder in OpenAPI spec file
        openapi_spec = replace_placeholder_in_file(ORGUNIT_OPENAPI_SPEC_PATH)
        if openapi_spec is None:
            logging.error(
                "Failed to load or replace placeholders in OpenAPI spec file: %s",
                ORGUNIT_OPENAPI_SPEC_PATH,
            )
            raise ValueError("Failed to process OpenAPI spec file.")

        # Log the loaded OpenAPI spec for debugging (optional)
        logging.debug("Processed OpenAPI Spec: %s", openapi_spec)

        # Fetch the latest organigram data
        latest_file = get_latest_json_file()
        logging.debug("Latest organigram data file: %s", latest_file)
        if not latest_file:
            raise FileNotFoundError("No organigram data available.")

        # Load the organigram data
        with open(
            os.path.join(JSON_DIR, latest_file), "r", encoding="utf-8"
        ) as json_file:
            data = json.load(json_file)
            return jsonify(data)

    except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
        logging.error("Specific error: %s", e)
        return abort(500, description=f"Internal server error: {e}")
    except OSError as e:
        logging.error("OS error: %s", e)
        return abort(500, description=f"Internal server error: {e}")


@blueprint.route(
    "/ris-synergy/v1/orgUnits/<orgunit_id>", methods=["GET"], endpoint="get_orgunit"
)
@swag_from(
    ORGUNIT_OPENAPI_SPEC_PATH,
    endpoint="ris-synergy.get_orgunit",
    methods=["GET"],
)
@enabled_endpoint("orgunit")
@keycloak_protected
@conditional_produces("application/json")
def get_orgunit(orgunit_id):
    """
    Get specific OrgUnit by ID
    This endpoint serves the data for a specific organizational unit based on its ID.
    """
    try:
        # Fetch the latest organigram data
        latest_file = get_latest_json_file()
        if not latest_file:
            raise FileNotFoundError("No organigram data available.")

        with open(
            os.path.join(JSON_DIR, latest_file), "r", encoding="utf-8"
        ) as json_file:
            data = json.load(json_file)
            # Filter the data to find the org unit with the given ID
            org_unit = next((item for item in data if item["id"] == orgunit_id), None)
            if not org_unit:
                raise ValueError(f"OrgUnit with ID {orgunit_id} not found.")
            return jsonify(org_unit)

    except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
        logging.error("Specific error: %s", e)
        return abort(500, description=f"Internal server error: {e}")
    except OSError as e:
        logging.error("OS error: %s", e)
        return abort(500, description=f"Internal server error: {e}")


@blueprint.route(
    "/ris-synergy/v1/orgUnits/organigram/<date>",
    methods=["GET"],
    endpoint="organigram_by_date",
)
@enabled_endpoint("orgunit")
@keycloak_protected
@conditional_produces("application/json")
def get_organigram_by_date(date):
    """
    Get Organigram Data for a Specific Date
    This endpoint serves the organizational tree of the university for a specific date.
    """
    try:
        # Validate the date format (YYYY-MM-DD)
        # Ensure the date parameter only contains valid characters
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            raise ValueError("Invalid date format. Use YYYY-MM-DD.")

        # Resolve the JSON directory path
        base_dir = Path(JSON_DIR).resolve()

        # Sanitize the filename part
        safe_date = secure_filename(f"organigram_{date}.json")

        # Construct the file path
        file_path = os.path.normpath(base_dir / safe_date).resolve()

        # Check if the resolved path is still within base_dir
        if not str(file_path).startswith(str(base_dir)):
            raise ValueError("Invalid date input.")

        # Ensure the file exists and is accessible
        if not file_path.is_file():
            raise FileNotFoundError(f"No organigram data available for {date}.")

        # Read and return the content of the file
        with file_path.open("r", encoding="utf-8") as json_file:
            data = json.load(json_file)
            return jsonify(data)

    except (json.JSONDecodeError, FileNotFoundError, ValueError, OSError) as e:
        logging.error("Error processing request: %s", e)
        return abort(500, description=f"Internal server error: {e}")


@blueprint.route("/ris-synergy/v1/projects/schema", methods=["GET"])
@enabled_endpoint("project")
@conditional_produces("application/json")
def get_project_schema():
    """
    Get Project JSON Schema
    This endpoint serves the JSON schema for projects.
    """
    try:
        schema = replace_placeholder_in_file(PROJECT_SCHEMA_PATH)
        if schema is None:
            return abort(500, description="Internal server error")
        return jsonify(schema)
    except (FileNotFoundError, ValueError, json.JSONDecodeError, yaml.YAMLError) as e:
        logging.error("Error fetching JSON schema: %s", e)
        return abort(500, description="Internal server error")


@blueprint.route("/ris-synergy/apidocs/project", methods=["GET"])
@enabled_endpoint("project")
@swag_from(PROJECT_OPENAPI_SPEC_PATH)
def show_projects_schema_apidocs():
    """
    Redirect to the Swagger UI with the search field pre-filled for project schema.
    """
    # Use url_for to dynamically build the path to the schema endpoint
    schema_url =  urljoin(OPEN_API_SERVER_URL, url_for("ris-synergy.get_project_schema"))
    # Redirect to the Flasgger documentation UI with the schema URL as a query parameter
    return redirect(f"/apidocs?url={schema_url}")
