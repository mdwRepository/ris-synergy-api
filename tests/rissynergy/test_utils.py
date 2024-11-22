# -*- coding: utf-8 -*-
"""
This module contains unit tests for the rissynergy utility functions.
"""

from unittest.mock import patch

import requests
from app.rissynergy.utils import download_json_data, validate_json_against_json_schema


def test_download_json_data_success():
    """
    Test successful JSON download from a URL.
    """
    mock_url = "https://api.example.com/data"
    mock_response = {"key": "value"}

    with patch("app.rissynergy.utils.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        result = download_json_data(mock_url)

        mock_get.assert_called_once_with(
            mock_url, headers={"Accept": "application/json"}, params={}, timeout=10
        )
        assert result == mock_response


def test_download_json_data_failure():
    """
    Test JSON download failure due to a non-200 status code.
    """
    mock_url = "https://api.example.com/data"

    with patch("app.rissynergy.utils.requests.get") as mock_get:
        mock_get.return_value.status_code = 404
        mock_get.return_value.text = "Not Found"

        result = download_json_data(mock_url)

        mock_get.assert_called_once_with(
            mock_url, headers={"Accept": "application/json"}, params={}, timeout=10
        )
        assert result is None


def test_download_json_data_request_exception():
    """
    Test JSON download failure due to a request exception.
    """
    mock_url = "https://api.example.com/data"

    with patch("app.rissynergy.utils.requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException("Connection error")

        result = download_json_data(mock_url)

        mock_get.assert_called_once_with(
            mock_url, headers={"Accept": "application/json"}, params={}, timeout=10
        )
        assert result is None


def test_validate_json_against_json_schema_valid():
    """
    Test successful JSON validation against a schema.
    """
    json_data = {"name": "John", "age": 30}
    json_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"},
        },
        "required": ["name", "age"],
    }

    result = validate_json_against_json_schema(json_data, json_schema)
    assert result is True


def test_validate_json_against_json_schema_invalid():
    """
    Test JSON validation failure due to a schema mismatch.
    """
    json_data = {"name": "John", "age": "thirty"}  # Age is a string instead of a number
    json_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"},
        },
        "required": ["name", "age"],
    }

    result, error_message = validate_json_against_json_schema(json_data, json_schema)
    assert result is False
    assert "is not of type 'number'" in error_message


def test_validate_json_against_json_schema_missing_required_field():
    """
    Test JSON validation failure due to missing required fields.
    """
    json_data = {"name": "John"}  # Missing the "age" field
    json_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"},
        },
        "required": ["name", "age"],
    }

    result, error_message = validate_json_against_json_schema(json_data, json_schema)
    assert result is False
    assert "'age' is a required property" in error_message


def test_validate_json_against_json_schema_value_error():
    """
    Test JSON validation failure due to a value error.
    """
    json_data = None
    json_schema = None

    result, error_message = validate_json_against_json_schema(json_data, json_schema)
    assert result is False
    assert "argument of type 'NoneType' is not iterable" in error_message


def test_validate_json_against_json_schema_schema_error():
    """
    Test JSON validation failure due to an invalid schema.
    """
    json_data = {"name": "John", "age": 30}
    json_schema = "This is not a valid JSON schema"  # Passing an invalid schema type

    result, error_message = validate_json_against_json_schema(json_data, json_schema)

    # Assertions
    assert result is False
    # Assert that the error message includes the invalid schema type explanation
    assert (
        "'This is not a valid JSON schema' is not of type 'object', 'boolean'"
        in error_message
    )


def test_validate_json_against_json_schema_type_error():
    """
    Test JSON validation failure due to a TypeError.
    """
    json_data = {"name": "John", "age": 30}  # Valid JSON data
    json_schema = 42  # Invalid JSON schema type (should be a dict)

    result, error_message = validate_json_against_json_schema(json_data, json_schema)

    # Assertions
    assert result is False
    assert (
        "argument of type 'int' is not iterable" in error_message
    )  # Check the actual error message
