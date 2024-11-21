# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

import logging
import json
import os
import re
import yaml

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    jsonify,
    abort,
    url_for,
    current_app,
)

from flask_negotiate import produces
from datetime import datetime
from flasgger import swag_from
from pathlib import Path
from werkzeug.utils import secure_filename

from app.decorators import keycloak_protected


static_url_path = os.getenv("STATIC_URL_PATH") or None
static_folder = os.getenv("STATIC_FOLDER") or None

logging.debug("static url path: ", static_url_path)
logging.debug("static folder: ", static_folder)

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
    "funding.yaml"  # Assuming this doesn't depend on version
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
    
    
def replace_placeholder_in_file(file_path, placeholder="{{SERVER_URL}}", replacement=OPEN_API_SERVER_URL):
    """
    Replace a placeholder in a JSON or YAML file with the given replacement.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace(placeholder, replacement)
        if file_path.endswith(".json"):
            return json.loads(content)
        elif file_path.endswith(".yaml") or file_path.endswith(".yml"):
            return yaml.safe_load(content)
        else:
            raise ValueError("Unsupported file type")
    except FileNotFoundError as e:
        logging.error(f"File not found: {file_path}")
        return None
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {e}")
        return None


@blueprint.route("/ris-synergy/ris_synergy.json", methods=["GET"])
@produces("application/json")
def get_ris_synergy_schema():
    """
    Get RIS Synergy JSON Schema
    This endpoint serves the JSON schema for the RIS Synergy endpoint.
    """
    try:
        schema = replace_placeholder_in_file(RIS_SYNERGY_SCHEMA_PATH)
        if schema is None:
            return abort(500, description="Internal server error")
        return jsonify(schema)
    except Exception as e:
        logging.error(f"Error fetching JSON schema: {e}")
        return abort(500, description="Internal server error")



@blueprint.route("/ris-synergy/v1/info/schema", methods=["GET"])
def get_info_schema():
    """
    Get Info JSON Schema
    Dynamically replaces placeholders with configured values.
    """
    try:
        schema = replace_placeholder_in_file(INFO_SCHEMA_PATH)
        if schema is None:
            return abort(500, description="Internal server error")
        return jsonify(schema)
    except Exception as e:
        logging.error(f"Error fetching JSON schema: {e}")
        return abort(500, description="Internal server error")


@blueprint.route("/ris-synergy/apidocs/info", methods=["GET"])
@swag_from(PROJECT_OPENAPI_SPEC_PATH)
def show_info_schema_apidocs():
    """
    Redirect to the Swagger UI with the search field pre-filled for info schema.
    """
    try:
        # Use url_for to dynamically build the path to the schema endpoint
        schema_url = url_for("ris-synergy.get_info_schema", _external=True)
        # Redirect to the Flasgger documentation UI with the schema URL as a query parameter
        return redirect(f"/apidocs?url={schema_url}")
    except Exception as e:
        logging.error(f"Error redirecting to Swagger UI: {e}")
        return abort(500, description="Internal server error")


@blueprint.route("/ris-synergy/v1/info", methods=["GET"], endpoint="info")
@swag_from(
    ORGUNIT_OPENAPI_SPEC_PATH,
    endpoint="ris-synergy.info",
    methods=["GET"],
)
@produces("application/json")
def get_info():
    """
    This endpoint serves the info data.
    """
    try:
        data = replace_placeholder_in_file(INFO_DATA_PATH)
        if data is None:
            return abort(500, description="Internal server error")
        return jsonify(data)
    except Exception as e:
        logging.error(f"Error fetching info data: {e}")
        return abort(500, description="Internal server error")
    

@blueprint.route("/ris-synergy/v1/orgUnits/organigram/schema", methods=["GET"])
@produces("application/json")
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
    except Exception as e:
        logging.error(f"Error fetching JSON schema: {e}")
        return abort(500, description="Internal server error")


@blueprint.route("/ris-synergy/apidocs/orgunit", methods=["GET"])
@swag_from(PROJECT_OPENAPI_SPEC_PATH)
def show_orgunits_schema_apidocs():
    """
    Redirect to the Swagger UI with the search field pre-filled for orgunit schema.
    """
    try:
        # Use url_for to dynamically build the path to the schema endpoint
        schema_url = url_for("ris-synergy.get_orgunit_schema", _external=True)
        # Redirect to the Flasgger documentation UI with the schema URL as a query parameter
        return redirect(f"/apidocs?url={schema_url}")
    except Exception as e:
        logging.error(f"Error redirecting to Swagger UI: {e}")
        return abort(500, description="Internal server error")


@blueprint.route(
    "/ris-synergy/v1/orgUnits/organigram", methods=["GET"], endpoint="organigram"
)
@swag_from(
    ORGUNIT_OPENAPI_SPEC_PATH,
    endpoint="ris-synergy.organigram",
    methods=["GET"],
)
@keycloak_protected
@produces("application/json")
def get_organigram():
    """
    Get Organigram Data
    This endpoint serves the organizational tree of the university.
    """
    try:
        # Replace placeholder in OpenAPI spec file
        openapi_spec = replace_placeholder_in_file(ORGUNIT_OPENAPI_SPEC_PATH)
        if openapi_spec is None:
            logging.error(f"Failed to load or replace placeholders in OpenAPI spec file: {ORGUNIT_OPENAPI_SPEC_PATH}")
            return abort(500, description="Internal server error: Failed to process OpenAPI spec file.")

        # Log the loaded OpenAPI spec for debugging (optional)
        logging.debug(f"Processed OpenAPI Spec: {openapi_spec}")

    except Exception as e:
        logging.error(f"Error loading OpenAPI spec: {e}")
        return abort(500, description="Internal server error while processing OpenAPI spec.")

    try:
        # Fetch the latest organigram data
        latest_file = get_latest_json_file()
        logging.debug(f"Latest organigram data file: {latest_file}")
        if not latest_file:
            return abort(404, description="No organigram data available.")
        
        # Load the organigram data
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
        return abort(500, description="Internal server error: Organigram file not found.")
    except Exception as e:
        logging.error(f"Error fetching organigram data or Swagger definition: {e}")
        return abort(500, description="Internal server error")


@blueprint.route(
    "/ris-synergy/v1/orgUnits/<id>", methods=["GET"], endpoint="get_orgunit"
)
@swag_from(
    ORGUNIT_OPENAPI_SPEC_PATH,
    endpoint="ris-synergy.get_orgunit",
    methods=["GET"],
)
@keycloak_protected
@produces("application/json")
def get_orgunit(id):
    """Get specific OrgUnit by ID
    This endpoint serves the data for a specific organizational unit based on its ID.
    """
    try:
        # Fetch the latest organigram data
        latest_file = get_latest_json_file()
        if not latest_file:
            return abort(404, description="No organigram data available.")
        
        with open(
            os.path.join(JSON_DIR, latest_file), "r", encoding="utf-8"
        ) as json_file:
            data = json.load(json_file)
            
        # Filter the data to find the org unit with the given ID
        org_unit = next((item for item in data if item["id"] == id), None)
        if not org_unit:
            return abort(404, description=f"OrgUnit with ID {id} not found.")
        
        return jsonify(org_unit)

    # Handle exceptions
    # Log the error and return an error response
    except json.JSONDecodeError as json_error:
        logging.error(f"Error decoding JSON: {json_error}")
        return abort(500, description="Internal server error: JSON decoding error.")
    except FileNotFoundError as fnf_error:
        logging.error(f"File not found: {fnf_error}")
        return abort(500, description="Internal server error")
    except Exception as e:
        logging.error(f"Error fetching OrgUnit data: {e}")
        return abort(500, description="Internal server error")


@blueprint.route(
    "/ris-synergy/v1/orgUnits/organigram/<date>", methods=["GET"], endpoint="organigram_by_date"
)
@keycloak_protected
@produces("application/json")
def get_organigram_by_date(date):
    """
    Get Organigram Data for a Specific Date
    This endpoint serves the organizational tree of the university for a specific date.
    """
    try:
        # Validate the date format (YYYY-MM-DD) 
        # Ensure the date parameter only contains valid characters
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
            return abort(400, description="Invalid date format. Use YYYY-MM-DD.")
               
        # Resolve the JSON directory path
        BASE_DIR = Path(JSON_DIR).resolve()

        # Sanitize the filename part
        safe_date = secure_filename(f"organigram_{date}.json")

        # Construct the file path
        file_path = os.path.normpath(BASE_DIR / safe_date).resolve()
        
        # Check if the resolved path is still within BASE_DIR
        if not str(file_path).startswith(str(BASE_DIR)):
            return abort(400, description="Invalid date input.")

        # Ensure the file exists and is accessible
        if not file_path.is_file():
            return abort(404, description=f"No organigram data available for {date}.")

        # Read and return the content of the file
        with file_path.open("r", encoding="utf-8") as json_file:
            data = json.load(json_file)
            return jsonify(data)

    # Handle exceptions
    # Log the error and return an error response
    except json.JSONDecodeError as json_error:
        logging.error(f"Error decoding JSON: {json_error}")
        return abort(500, description="Internal server error: JSON decoding error.")
    except Exception as e:
        logging.error(f"Error fetching organigram data for date {date}: {e}")
        return abort(500, description="Internal server error")


@blueprint.route("/ris-synergy/v1/projects/schema", methods=["GET"])
@produces("application/json")
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
    except Exception as e:
        logging.error(f"Error fetching JSON schema: {e}")
        return abort(500, description="Internal server error")


@blueprint.route("/ris-synergy/apidocs/project", methods=["GET"])
@swag_from(PROJECT_OPENAPI_SPEC_PATH)
def show_projects_schema_apidocs():
    """
    Redirect to the Swagger UI with the search field pre-filled for project schema.
    """
    try:
        # Use url_for to dynamically build the path to the schema endpoint
        schema_url = url_for("ris-synergy.get_project_schema", _external=True)
        # Redirect to the Flasgger documentation UI with the schema URL as a query parameter
        return redirect(f"/apidocs?url={schema_url}")
    except Exception as e:
        logging.error(f"Error redirecting to Swagger UI: {e}")
        return abort(500, description="Internal server error")
