# -*- coding: utf-8 -*-
"""
Module: merge_openapi_utils.py

Utility functions for processing, merging, and handling OpenAPI specifications in JSON or YAML format.

Functions:
- `preprocess_yaml_content`: Replaces placeholders in YAML content with specified values.
- `merge_components`: Merges `components` sections from OpenAPI specifications.
- `merge_paths`: Merges `paths` sections from OpenAPI specifications.
- `load_and_merge_file`: Loads an OpenAPI specification from JSON or YAML and merges it into the specified object.
"""

import json
from pathlib import Path
import yaml


def preprocess_yaml_content(content, placeholder, replacement):
    """
    Replaces placeholders in YAML content with the specified replacement value.
    
    Parameters:
    - content (str): Raw YAML content.
    - placeholder (str): Placeholder string to replace.
    - replacement (str): Replacement value.

    Returns:
    - str: Processed YAML content.
    """
    return content.replace(placeholder, replacement)


def merge_components(merged, new_components):
    """
    Merges OpenAPI components from `new_components` into `merged`.

    Parameters:
    - merged (dict): Existing merged components.
    - new_components (dict): Components to be added.
    """
    for comp_type, comp_data in new_components.items():
        if comp_type not in merged:
            merged[comp_type] = comp_data
        else:
            merged[comp_type].update(comp_data)


def merge_paths(merged, new_paths):
    """
    Merges OpenAPI paths from `new_paths` into `merged`.

    Parameters:
    - merged (dict): Existing merged paths.
    - new_paths (dict): Paths to be added.
    """
    merged.update(new_paths)


def load_and_merge_file(file_path, merged_api, preprocess_fn=None):
    """
    Loads an OpenAPI specification file and merges its content into `merged_api`.

    Parameters:
    - file_path (str or Path): Path to the OpenAPI file.
    - merged_api (dict): Existing merged OpenAPI specification.
    - preprocess_fn (callable, optional): Function to preprocess raw content.

    Features:
    - Handles both JSON and YAML file formats.
    - Supports placeholder replacement during preprocessing.
    - Merges `paths` and `components` sections of the OpenAPI specification.

    Warnings:
    - Logs a warning if the file is not found.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"Warning: File not found - {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        raw_content = f.read()
        if preprocess_fn:
            raw_content = preprocess_fn(raw_content)
        api_data = (
            json.loads(raw_content)
            if file_path.suffix == ".json"
            else yaml.safe_load(raw_content)
        )

        if "paths" in api_data:
            merge_paths(merged_api["paths"], api_data["paths"])

        if "components" in api_data:
            if "components" not in merged_api:
                merged_api["components"] = api_data["components"]
            else:
                merge_components(merged_api["components"], api_data["components"])
