# -*- coding: utf-8 -*-
"""
Module: utils.py

This module provides utility functions for working with JSON data, including 
downloading JSON from a URL and validating JSON data against a JSON schema.

Functions:
- `download_json_data(url, params={})`:
  Downloads JSON data from the specified URL using an HTTP GET request. 
  Supports optional query parameters.

  Parameters:
    - `url` (str): The URL to fetch data from.
    - `params` (dict): Optional query parameters to include in the request.

  Returns:
    - `dict`: Parsed JSON data if the request is successful.
    - `None`: If an error occurs or the response status is not 200.

  Logs:
    - Response status and text for debugging.
    - Errors encountered during the request.

- `validate_json_against_json_schema(json_data, json_schema)`:
  Validates JSON data against a provided JSON schema using the `jsonschema` library.

  Parameters:
    - `json_data` (dict): The JSON data to validate.
    - `json_schema` (dict): The JSON schema to validate against.

  Returns:
    - `True`: If the JSON data is valid.
    - `False`: If the validation fails or an error occurs.

  Logs:
    - Validation errors and other exceptions.

Dependencies:
- `requests`: For making HTTP GET requests.
- `jsonschema.validate`: For validating JSON data against schemas.

Usage:
This module is intended for use in applications that require JSON data validation 
and retrieval from external APIs or resources.

Example:
    url = "https://api.example.com/data"
    json_data = download_json_data(url)
    if json_data:
        schema = {...}  # Define your JSON schema
        is_valid = validate_json_against_json_schema(json_data, schema)
        if is_valid:
            print("JSON data is valid")
        else:
            print("JSON data is invalid")
"""


import requests

from jsonschema import validate


def download_json_data(url, params={}):
    """
    Download JSON data from a URL.
    """
    try:
        headers = {
            "Accept": "application/json",
        }
        response = requests.get(url, headers=headers, params=params)
        print(f"Response: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            return response.json()
        else:
            # print response.status_code and error message
            print(f"Error: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def validate_json_against_json_schema(json_data, json_schema):
    """
    Validate JSON data against a JSON schema.
    """
    try:
        # validate json_data against json_schema
        print("Validating JSON data against JSON schema")
        validate(instance=json_data, schema=json_schema)
        return True
    except validate.ValidationError as e:
        print(f"Validation Error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
