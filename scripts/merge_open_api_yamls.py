# -*- coding: utf-8 -*-
"""
Script: merge_open_api_yamls.py

This script consolidates multiple OpenAPI specification YAML files into a single cohesive 
OpenAPI YAML file. The script allows customization of the merged API's title, description, 
version, and server URL during the merging process.

Key Features:
- Combines OpenAPI paths, components, and other sections from multiple files.
- Replaces placeholders (e.g., {{SERVER_URL}}) in the source YAML files with a specified value.
- Outputs a unified OpenAPI YAML file ready for use.

Constants:
- `TITLE` (str): Default title for the merged OpenAPI specification.
- `DESCRIPTION` (str): Default description for the merged API.
- `VERSION` (str): Default version for the merged API.
- `OPEN_API_SERVER_URL` (str): Base server URL for the OpenAPI specification.
- `BASE_DIR` (Path): Base directory for the source YAML files.
- `INPUT_FILE_PATHS` (list of Path): List of file paths to the source OpenAPI YAML files.
- `OUTPUT_FILE` (Path): Path to save the merged OpenAPI specification.

Dependencies:
- `yaml`: For parsing and writing YAML files.
- `pathlib.Path`: For handling file paths in a platform-independent manner.
- `merge_openapi_utils`: A custom module providing helper functions for processing and 
  merging OpenAPI YAML files.

Functions:
- `merge_openapi_files`: 
    Merges multiple OpenAPI YAML files into one unified OpenAPI specification.

Usage:
Run the script directly to merge predefined OpenAPI YAML files and save the result to a 
specified output file:

    python merge_open_api_yamls.py

The script uses default constants for input file paths, output file paths, and OpenAPI 
metadata. Update the constants or extend the script for custom use cases.

"""


from pathlib import Path
import yaml

from merge_openapi_utils import load_and_merge_file, preprocess_yaml_content

TITLE = "RIS Synergy API"
DESCRIPTION = "Full API for RIS Synergy"
VERSION = "1.0"
OPEN_API_SERVER_URL = "https://default-url.com"
# Base directory for app folder
BASE_DIR = Path(__file__).resolve().parent.parent / "app"
INPUT_FILE_PATHS = [
        BASE_DIR
        / "rissynergy"
        / "openapi"
        / f"RIS-SYNERGY-info-api-{VERSION}-swagger.yaml",
        BASE_DIR
        / "rissynergy"
        / "openapi"
        / f"RIS-SYNERGY-org-unit_api-{VERSION}-swagger.yaml",
        BASE_DIR
        / "rissynergy"
        / "openapi"
        / f"RIS-SYNERGY-project-api-{VERSION}-swagger.yaml",
    ]
OUTPUT_FILE = BASE_DIR / "rissynergy" / "openapi" / f"ris-synergy-{VERSION}.yaml"


def merge_openapi_files(file_paths, output_file, new_title, new_description, version):
    """
    Merges multiple OpenAPI YAML files into one cohesive specification.

    Parameters:
    - file_paths (list of str): List of paths to the OpenAPI YAML files to merge.
    - output_file (str): Path to save the merged OpenAPI YAML file.
    - new_title (str): Title for the merged OpenAPI specification.
    - new_description (str): Description for the merged OpenAPI specification.
    - version (str): Version for the merged OpenAPI specification.
    """
    merged_api = {
        "openapi": "3.0.1",
        "info": {
            "title": new_title,
            "description": new_description,
            "version": version,
        },
        "servers": [{"url": f"{OPEN_API_SERVER_URL}/ris-synergy"}],
        "paths": {},
        "components": {},
    }

    for file_path in file_paths:

        def preprocess_fn(content):
            return preprocess_yaml_content(
                content, "{{SERVER_URL}}", OPEN_API_SERVER_URL
            )

        load_and_merge_file(file_path, merged_api, preprocess_fn)

    # Save merged API to the output YAML file
    output_file = Path(output_file)
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(merged_api, f, default_flow_style=False)
    print(f"Merged API saved to {output_file}")


if __name__ == "__main__":
    merge_openapi_files(INPUT_FILE_PATHS, OUTPUT_FILE, TITLE, DESCRIPTION, VERSION)
