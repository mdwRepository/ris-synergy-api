# -*- coding: utf-8 -*-
"""
Script: merge_open_api_jsons.py

This script consolidates multiple OpenAPI specification JSON files into a single cohesive 
OpenAPI JSON file. The script supports customization of the merged API's title, description, 
version, and server URL.

Key Features:
- Combines OpenAPI paths, components, and other sections from multiple JSON files.
- Customizes the merged specification with user-defined metadata (title, description, version).
- Outputs a unified OpenAPI JSON file that adheres to the OpenAPI 3.0.1 specification.

Constants:
- `TITLE` (str): Default title for the merged OpenAPI specification.
- `DESCRIPTION` (str): Default description for the merged API.
- `VERSION` (str): Default version for the merged API.
- `OPEN_API_SERVER_URL` (str): Base server URL for the OpenAPI specification.
- `BASE_DIR` (Path): Base directory for the source JSON files.
- `INPUT_FILE_PATHS` (list of Path): List of file paths to the source OpenAPI JSON files.
- `OUTPUT_FILE` (Path): Path to save the merged OpenAPI specification.

Dependencies:
- `json`: For parsing and writing JSON files.
- `pathlib.Path`: For handling file paths in a platform-independent manner.
- `merge_openapi_utils`: A custom module providing helper functions for processing and 
  merging OpenAPI JSON files.

Functions:
- `merge_openapi_files`:
    Merges multiple OpenAPI JSON files into one cohesive OpenAPI specification.

Usage:
Run the script directly to merge predefined OpenAPI JSON files and save the result to a 
specified output file:

    python merge_open_api_jsons.py

The script uses default constants for input file paths, output file paths, and OpenAPI 
metadata. Update the constants or extend the script for custom use cases.

"""
