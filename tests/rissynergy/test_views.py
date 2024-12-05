"""
Module for testing rissynergy views.
"""

import os
import json
import yaml
import pytest
import logging
from unittest.mock import mock_open, patch
from flask import Flask, jsonify, request, url_for

from app.rissynergy.views import (
    blueprint,
    is_valid_yaml,
    get_latest_json_file,
    replace_placeholder_in_file,
    INFO_OPENAPI_SPEC_PATH,
    PROJECT_OPENAPI_SPEC_PATH,
    ORGUNIT_OPENAPI_SPEC_PATH,
)


@pytest.fixture
def override_env(monkeypatch):
    """Fixture to override the OPEN_API_SERVER_URL environment variable."""
    monkeypatch.setenv("OPEN_API_SERVER_URL", "http://localhost")


@pytest.fixture
def app_with_blueprint():
    """Fixture to create a Flask app with the public blueprint."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(blueprint)
    return app


# Test cases for `is_valid_yaml`
def test_is_valid_yaml_valid_file():
    """Test is_valid_yaml with a valid YAML file."""
    valid_yaml_content = "key: value\nlist:\n  - item1\n  - item2"
    with patch("builtins.open", mock_open(read_data=valid_yaml_content)):
        assert is_valid_yaml("test.yaml") is True


def test_is_valid_yaml_invalid_file():
    """Test is_valid_yaml with an invalid YAML file."""
    invalid_yaml_content = "key: value\nlist:\n  - item1\n  - item2: :"
    with patch("builtins.open", mock_open(read_data=invalid_yaml_content)):
        assert is_valid_yaml("test.yaml") is False


def test_is_valid_yaml_file_not_found():
    """Test is_valid_yaml when the file does not exist."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        assert is_valid_yaml("nonexistent.yaml") is False


# Test cases for `get_latest_json_file`
def test_get_latest_json_file_valid():
    """Test get_latest_json_file with valid files in the directory."""
    mock_files = ["organigram_202311.json", "organigram_202310.json"]
    with patch("os.listdir", return_value=mock_files):
        with patch("os.path.isdir", return_value=True):
            assert get_latest_json_file() == "organigram_202311.json"


def test_get_latest_json_file_no_files():
    """Test get_latest_json_file when no matching files are found."""
    with patch("os.listdir", return_value=[]):
        assert get_latest_json_file() is None


def test_get_latest_json_file_directory_not_found():
    """Test get_latest_json_file when JSON_DIR does not exist."""
    with patch("os.listdir", side_effect=FileNotFoundError):
        assert get_latest_json_file() is None


def test_get_latest_json_file_permission_error():
    """Test get_latest_json_file when JSON_DIR has permission issues."""
    with patch("os.listdir", side_effect=PermissionError):
        assert get_latest_json_file() is None


# Test cases for `replace_placeholder_in_file`
"""
def test_replace_placeholder_in_json(override_env):
    # Test replace_placeholder_in_file for JSON files.
    json_content = '{"key": "{{SERVER_URL}}"}'
    expected_result = {"key": "http://localhost"}

    with patch("builtins.open", mock_open(read_data=json_content)), patch(
        "app.rissynergy.views.OPEN_API_SERVER_URL", os.getenv("OPEN_API_SERVER_URL")
    ):
        result = replace_placeholder_in_file("test.json")
        assert result == expected_result


def test_replace_placeholder_in_yaml(override_env):
    # Test replace_placeholder_in_file for YAML files.
    yaml_content = "key: {{SERVER_URL}}"
    expected_result = {"key": "http://localhost"}

    with patch("builtins.open", mock_open(read_data=yaml_content)), patch(
        "app.rissynergy.views.OPEN_API_SERVER_URL", os.getenv("OPEN_API_SERVER_URL")
    ):
        result = replace_placeholder_in_file("test.yaml")
        assert result == expected_result
"""


def test_replace_placeholder_file_not_found():
    """Test replace_placeholder_in_file when the file does not exist."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        assert replace_placeholder_in_file("nonexistent.json") is None


def test_replace_placeholder_unsupported_file_type():
    """Test replace_placeholder_in_file for unsupported file types."""
    with patch("builtins.open", mock_open(read_data="dummy content")):
        assert replace_placeholder_in_file("test.txt") is None


def test_replace_placeholder_invalid_json():
    """Test replace_placeholder_in_file with invalid JSON content."""
    invalid_json_content = '{"key": {{SERVER_URL}}}'
    with patch("builtins.open", mock_open(read_data=invalid_json_content)):
        assert replace_placeholder_in_file("test.json") is None


def test_replace_placeholder_invalid_yaml():
    """Test replace_placeholder_in_file with invalid YAML content."""
    invalid_yaml_content = "key: {{SERVER_URL}:"
    with patch("builtins.open", mock_open(read_data=invalid_yaml_content)):
        assert replace_placeholder_in_file("test.yaml") is None


def test_replace_placeholder_os_error():
    """Test replace_placeholder_in_file with an OS error."""
    with patch("builtins.open", side_effect=OSError):
        assert replace_placeholder_in_file("test.json") is None


# Test cases for `get_ris_synergy_schema` route
def test_get_ris_synergy_schema_success(app_with_blueprint):
    """Test the get_ris_synergy_schema endpoint successfully returns schema."""
    mock_schema = {"type": "object", "properties": {"key": {"type": "string"}}}

    with patch(
        "app.rissynergy.views.replace_placeholder_in_file", return_value=mock_schema
    ):
        with patch("app.rissynergy.views.RIS_SYNERGY_SCHEMA_PATH", "mock_schema_path"):
            with app_with_blueprint.test_client() as client:
                response = client.get(
                    "/ris-synergy/ris_synergy.json",
                    headers={"Accept": "application/json"},
                )

                assert response.status_code == 200
                assert response.get_json() == mock_schema


def test_get_ris_synergy_schema_file_not_found(app_with_blueprint):
    """Test the get_ris_synergy_schema endpoint when file is not found."""
    with patch("builtins.open", side_effect=FileNotFoundError()):
        with patch("app.rissynergy.views.RIS_SYNERGY_SCHEMA_PATH", "non_existent_path"):
            with app_with_blueprint.test_client() as client:
                response = client.get(
                    "/ris-synergy/ris_synergy.json",
                    headers={"Accept": "application/json"},
                )

                assert response.status_code == 500
                assert response.get_json() == {"error": "Internal server error"}


def test_get_ris_synergy_schema_invalid_json(app_with_blueprint):
    """Test the get_ris_synergy_schema endpoint with invalid JSON."""
    invalid_json = '{"type": "object", "properties": {"key": {"type": "string"}}'  # Missing closing brace

    with patch("builtins.open", mock_open(read_data=invalid_json)):
        with patch("app.rissynergy.views.RIS_SYNERGY_SCHEMA_PATH", "mock_schema_path"):
            with app_with_blueprint.test_client() as client:
                response = client.get(
                    "/ris-synergy/ris_synergy.json",
                    headers={"Accept": "application/json"},
                )

                assert response.status_code == 500
                assert response.get_json() == {"error": "Internal server error"}


def test_get_ris_synergy_schema_value_error(app_with_blueprint):
    """Test the get_ris_synergy_schema endpoint with a ValueError in processing."""
    with patch("builtins.open", mock_open(read_data="{}")):
        with patch("app.rissynergy.views.RIS_SYNERGY_SCHEMA_PATH", "mock_schema_path"):
            with patch(
                "app.rissynergy.views.replace_placeholder_in_file",
                side_effect=ValueError("Invalid value"),
            ):
                with app_with_blueprint.test_client() as client:
                    response = client.get(
                        "/ris-synergy/ris_synergy.json",
                        headers={"Accept": "application/json"},
                    )

                    assert response.status_code == 500
                    assert response.get_json() == {"error": "Internal server error"}


def test_get_info_schema_success(app_with_blueprint):
    """Test the get_info_schema endpoint successfully returns schema."""
    mock_schema = {"type": "object", "properties": {"info": {"type": "string"}}}
    with patch(
        "app.rissynergy.views.replace_placeholder_in_file", return_value=mock_schema
    ):
        with patch("app.rissynergy.views.INFO_SCHEMA_PATH", "mock_info_schema_path"):
            with app_with_blueprint.test_client() as client:
                response = client.get(
                    "/ris-synergy/v1/info/schema",
                    headers={"Accept": "application/json"},
                )
                assert response.status_code == 200
                assert response.get_json() == mock_schema


def test_get_info_schema_file_not_found(app_with_blueprint):
    """Test the get_info_schema endpoint when the schema file is not found."""
    with patch("builtins.open", side_effect=FileNotFoundError()):
        with patch(
            "app.rissynergy.views.INFO_SCHEMA_PATH", "non_existent_info_schema_path"
        ):
            with app_with_blueprint.test_client() as client:
                response = client.get(
                    "/ris-synergy/v1/info/schema",
                    headers={"Accept": "application/json"},
                )
                assert response.status_code == 500
                assert response.json["error"] == "Internal server error"


def test_get_info_schema_invalid_json(app_with_blueprint):
    """Test the get_info_schema endpoint with invalid JSON."""
    invalid_json = '{"type": "object", "properties": {"info": {"type": "string"}}'  # Missing closing brace
    with patch("builtins.open", mock_open(read_data=invalid_json)):
        with patch("app.rissynergy.views.INFO_SCHEMA_PATH", "mock_info_schema_path"):
            with app_with_blueprint.test_client() as client:
                response = client.get(
                    "/ris-synergy/v1/info/schema",
                    headers={"Accept": "application/json"},
                )
                assert response.status_code == 500
                assert response.json["error"] == "Internal server error"


def test_get_info_schema_value_error(app_with_blueprint):
    """Test the get_info_schema endpoint with a ValueError."""
    with patch("builtins.open", mock_open(read_data="{}")):
        with patch("app.rissynergy.views.INFO_SCHEMA_PATH", "mock_info_schema_path"):
            with patch(
                "app.rissynergy.views.replace_placeholder_in_file",
                side_effect=ValueError("Invalid value"),
            ):
                with app_with_blueprint.test_client() as client:
                    response = client.get(
                        "/ris-synergy/v1/info/schema",
                        headers={"Accept": "application/json"},
                    )
                    assert response.status_code == 500
                    assert response.json["error"] == "Internal server error"


def test_show_info_schema_apidocs_redirect(app_with_blueprint):
    """Test the show_info_schema_apidocs route for redirection."""
    with app_with_blueprint.test_client() as client:
        with patch("app.rissynergy.views.url_for") as mock_url_for:
            mock_url_for.return_value = "http://localhost/ris-synergy/v1/info/schema"

            response = client.get("/ris-synergy/apidocs/info")

            # Assert the response is a redirect
            assert response.status_code == 302

            # Assert redirection URL contains the schema URL as a query parameter
            assert response.headers["Location"].startswith("/apidocs?url=")
            assert (
                "http://localhost/ris-synergy/v1/info/schema"
                in response.headers["Location"]
            )


def test_show_orgunits_schema_apidocs_redirect(app_with_blueprint):
    """Test that the route redirects to Swagger UI with the correct schema URL."""
    with app_with_blueprint.test_client() as client:
        # Mock `url_for` to return a known schema URL
        with patch(
            "app.rissynergy.views.url_for",
            return_value="http://localhost/ris-synergy/v1/orgUnits/schema",
        ):
            response = client.get("/ris-synergy/apidocs/orgunit")

            # Assert the response is a redirect
            assert response.status_code == 302

            # Assert redirection URL contains the schema URL as a query parameter
            assert response.headers["Location"].startswith("/apidocs?url=")
            assert (
                "http://localhost/ris-synergy/v1/orgUnits/schema"
                in response.headers["Location"]
            )


def test_show_projects_schema_apidocs_redirect(app_with_blueprint):
    """Test that the route redirects to Swagger UI with the correct schema URL."""
    with app_with_blueprint.test_client() as client:
        # Mock `url_for` to return a known schema URL
        with patch(
            "app.rissynergy.views.url_for",
            return_value="http://localhost/ris-synergy/v1/projects/schema",
        ):
            response = client.get("/ris-synergy/apidocs/project")

            # Assert the response is a redirect
            assert response.status_code == 302

            # Assert redirection URL contains the schema URL as a query parameter
            assert response.headers["Location"].startswith("/apidocs?url=")
            assert (
                "http://localhost/ris-synergy/v1/projects/schema"
                in response.headers["Location"]
            )


def test_get_info_success(app_with_blueprint):
    """Test the get_info endpoint successfully returns data."""
    mock_data = {"info": "data"}
    mock_data_json = '{"info": "data"}'

    # Use a proper file extension to avoid "Unsupported file type" error
    with patch("builtins.open", mock_open(read_data=mock_data_json)):
        with patch("app.rissynergy.views.INFO_DATA_PATH", "mock_info_data.json"):
            with app_with_blueprint.test_client() as client:
                response = client.get(
                    "/ris-synergy/v1/info", headers={"Accept": "application/json"}
                )

                assert response.status_code == 200
                assert response.get_json() == mock_data
