# -*- coding: utf-8 -*-
"""
This module contains tests for the logging setup.
"""

import os
from unittest.mock import patch
import pytest
from app.logging_setup import create_log_folder


@pytest.fixture
def mock_log_folder_env():
    """
    Fixture to set the LOG_FOLDER environment variable for testing.
    """
    log_folder = "test_logs"
    os.environ["LOG_FOLDER"] = log_folder
    yield log_folder
    del os.environ["LOG_FOLDER"]


def test_create_log_folder_creation(mock_log_folder_env):
    """
    Test that create_log_folder creates the log folder when it does not exist.
    """
    log_folder = mock_log_folder_env

    # Ensure the folder doesn't exist initially
    if os.path.exists(log_folder):
        os.rmdir(log_folder)

    # Mock os.makedirs
    with patch("os.makedirs") as mock_makedirs, patch("builtins.print") as mock_print:
        create_log_folder()

        # Assert os.makedirs was called
        mock_makedirs.assert_called_once_with(log_folder)

        # Assert the appropriate message was printed
        mock_print.assert_called_once_with(f"Info: log folder {log_folder} created")


def test_create_log_folder_exists(mock_log_folder_env):
    """
    Test that create_log_folder recognizes an existing folder and doesn't attempt to recreate it.
    """
    log_folder = mock_log_folder_env

    # Ensure the folder exists initially
    os.makedirs(log_folder, exist_ok=True)

    # Mock os.makedirs
    with patch("os.makedirs") as mock_makedirs, patch("builtins.print") as mock_print:
        create_log_folder()

        # Assert os.makedirs was not called
        mock_makedirs.assert_not_called()

        # Assert the appropriate message was printed
        mock_print.assert_called_once_with(f"Info: log folder {log_folder} exists")

    # Cleanup after test
    if os.path.exists(log_folder):
        os.rmdir(log_folder)
