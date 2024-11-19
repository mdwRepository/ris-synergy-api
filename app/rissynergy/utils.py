# -*- coding: utf-8 -*-

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
