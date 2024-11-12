# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

import logging
import json
import os
import yaml

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    jsonify,
    abort,
    url_for,
)

from flask_negotiate import produces
from datetime import datetime
from flasgger import swag_from

from app.decorators import set_theme


static_url_path = os.getenv("STATIC_URL_PATH") or None
static_folder = os.getenv("STATIC_FOLDER") or None

logging.debug("static url path: ", static_url_path)
logging.debug("static folder: ", static_folder)

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
    "SZEPESTEFAN-org-unit_api-1.0-resolved.json",
)
INFO_SCHEMA_PATH = os.path.join(
    os.getcwd(),
    "app",
    "rissynergy",
    "jsonschemas",
    "SZEPESTEFAN-info-api-1.0-resolved.json",
)
FUNDING_SCHEMA_PATH = os.path.join(
    os.getcwd(), "app", "rissynergy", "jsonschemas", "funding-v.1.0.0.json"
)
PROJECT_SCHEMA_PATH = os.path.join(
    os.getcwd(),
    "app",
    "rissynergy",
    "jsonschemas",
    "SZEPESTEFAN-project-api-1.0-resolved.json",
)
ORGUNIT_OPENAPI_SPEC_PATH = os.path.join(
    os.getcwd(),
    "app",
    "rissynergy",
    "openapi",
    "SZEPESTEFAN-org-unit_api-1.0-resolved.yaml",
)
INFO_OPENAPI_SPEC_PATH = os.path.join(
    os.getcwd(),
    "app",
    "rissynergy",
    "openapi",
    "SZEPESTEFAN-info-api-1.0-resolved.yaml",
)
FUNDING_OPENAPI_SPEC_PATH = os.path.join(
    os.getcwd(), "app", "rissynergy", "openapi", "funding.yaml"
)
PROJECT_OPENAPI_SPEC_PATH = os.path.join(
    os.getcwd(),
    "app",
    "rissynergy",
    "openapi",
    "SZEPESTEFAN-project-api-1.0-resolved.yaml",
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
        with open(file_path, "r") as file:
            yaml.safe_load(file)  # Try to parse the YAML file
        return True
    except yaml.YAMLError as e:
        logging.error(f"Invalid YAML in {file_path}: {e}")
        return False
    except FileNotFoundError as e:
        logging.error(f"Error reading {file_path}: {e}")
        return False
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return False


def get_latest_json_file():
    """
    Get the latest JSON file in the JSON_DIR directory.
    """
    try:
        # Get all JSON files with the naming pattern organigram_YYYY-MM-DD.json
        files = [
            f
            for f in os.listdir(JSON_DIR)
            if f.startswith("organigram_") and f.endswith(".json")
        ]
        # Sort files by date based on the filename
        files.sort(reverse=True)
        if not files:
            raise FileNotFoundError("No JSON files found.")
        return files[0]
    except Exception as e:
        logging.error(f"Error getting latest JSON file: {e}")
        return None


@blueprint.route("/ris-synergy/ris_synergy.json", methods=["GET"])
def get_ris_synergy_schema():
    """
    Get RIS Synergy JSON Schema
    This endpoint serves the JSON schema for the RIS Synergy endpoint.
    """
    try:
        # Open and read the JSON schema file
        with open(RIS_SYNERGY_SCHEMA_PATH, "r") as schema_file:
            schema = json.load(schema_file)

        # Return the schema as a JSON response
        return jsonify(schema)

    except FileNotFoundError:
        logging.error(f"JSON schema file not found: {RIS_SYNERGY_SCHEMA_PATH}")
        return abort(404, description="JSON schema file not found")

    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON schema: {e}")
        return abort(500, description="Error decoding JSON schema")

    except Exception as e:
        logging.error(f"Error fetching JSON schema: {e}")
        return abort(500, description="Internal server error")


@blueprint.route("/ris-synergy/v1/info/schema", methods=["GET"])
def get_info_schema():
    """
    Get Info JSON Schema
    This endpoint serves the JSON schema for the info endpoint.
    """
    try:
        with open(INFO_SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
            schema = json.load(schema_file)
        return jsonify(schema)
    except Exception as e:
        logging.error(f"Error fetching JSON schema: {e}")
        return abort(500, description="Internal server error")


@blueprint.route("/ris-synergy/apidocs/orgunit", methods=["GET"])
@swag_from(PROJECT_OPENAPI_SPEC_PATH)
def show_info_schema_apidocs():
    """
    Redirect to the Swagger UI with the search field pre-filled for info schema.
    """
    # Use url_for to dynamically build the path to the schema endpoint
    schema_url = url_for("ris-synergy.get_info_schema", _external=True)
    # Redirect to the Flasgger documentation UI with the schema URL as a query parameter
    return redirect(f"/apidocs?url={schema_url}")


@blueprint.route("/ris-synergy/v1/orgUnits/organigram/schema", methods=["GET"])
def get_orgunit_schema():
    """
    Get OrgUnit JSON Schema
    This endpoint serves the JSON schema for organizational units.
    """
    try:
        with open(ORGUNIT_SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
            schema = json.load(schema_file)
        return jsonify(schema)
    except Exception as e:
        logging.error(f"Error fetching JSON schema: {e}")
        return abort(500, description="Internal server error")


@blueprint.route("/ris-synergy/apidocs/orgunit", methods=["GET"])
@swag_from(PROJECT_OPENAPI_SPEC_PATH)
def show_orgunits_schema_apidocs():
    """
    Redirect to the Swagger UI with the search field pre-filled for orgunit schema.
    """
    # Use url_for to dynamically build the path to the schema endpoint
    schema_url = url_for("ris-synergy.get_orgunit_schema", _external=True)
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
def get_organigram():
    """Get Organigram Data
    This endpoint serves the organizational tree of the university.
    """
    # Debug to check if the file exists
    if not os.path.exists(ORGUNIT_OPENAPI_SPEC_PATH):
        logging.error(f"OpenAPI spec file not found: {ORGUNIT_OPENAPI_SPEC_PATH}")
        return abort(
            500, description="Internal server error: OpenAPI spec file not found."
        )

    # Log the loaded OpenAPI spec path and content (for debugging purposes)
    with open(ORGUNIT_OPENAPI_SPEC_PATH, "r", encoding="utf-8") as f:
        spec_content = f.read()
        logging.debug(f"Loaded OpenAPI Spec: {spec_content}")

    # Check if the OpenAPI spec file is a valid YAML file
    if not is_valid_yaml(ORGUNIT_OPENAPI_SPEC_PATH):
        return abort(
            500,
            description="Internal server error: Invalid YAML format in OpenAPI spec.",
        )

    try:
        # Fetch the latest organigram data
        latest_file = get_latest_json_file()
        logging.debug("latest_file: ", latest_file)
        if not latest_file:
            return abort(404, description="No organigram data available.")
        with open(
            os.path.join(JSON_DIR, latest_file), "r", encoding="utf-8"
        ) as json_file:
            data = json.load(json_file)
            return jsonify(data)
    except json.JSONDecodeError as json_error:
        logging.error(f"Error decoding JSON: {json_error}")
        return abort(500, description="Internal server error: JSON decoding error.")
    except FileNotFoundError as fnf_error:
        logging.error(f"File not found: {fnf_error}")
        return abort(500, description="Internal server error")
    except Exception as e:
        logging.error(f"Error fetching organigram data or Swagger definition: {e}")
        return abort(500, description="Internal server error")


@blueprint.route("/ris-synergy/v1/projects/schema", methods=["GET"])
def get_project_schema():
    """
    Get Project JSON Schema
    This endpoint serves the JSON schema for projects.
    """
    try:
        with open(PROJECT_SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
            schema = json.load(schema_file)
        return jsonify(schema)
    except Exception as e:
        logging.error(f"Error fetching JSON schema: {e}")
        return abort(500, description="Internal server error")


@blueprint.route("/ris-synergy/apidocs/project", methods=["GET"])
@swag_from(PROJECT_OPENAPI_SPEC_PATH)
def show_projects_schema_apidocs():
    """
    Redirect to the Swagger UI with the search field pre-filled for project schema.
    """
    # Use url_for to dynamically build the path to the schema endpoint
    schema_url = url_for("ris-synergy.get_project_schema", _external=True)
    # Redirect to the Flasgger documentation UI with the schema URL as a query parameter
    return redirect(f"/apidocs?url={schema_url}")
