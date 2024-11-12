# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

import logging
import json
import os
import yaml

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    abort,
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