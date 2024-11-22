# -*- coding: utf-8 -*-
"""
Module: logging_setup.py

This module configures logging for the Flask application. It provides utilities
to set up logging to files and the console, ensuring log messages are formatted
and handled consistently across the application.

Functions:
- `set_log_level()`: Determines the log level based on the `LOG_LEVEL` environment
  variable, defaulting to `INFO` if not specified.
- `setup_file_handler()`: Configures a file handler for logging, with log rotation
  enabled, and applies a consistent log message format.
- `setup_stream_handler()`: Configures a stream handler for console logging, 
  applying a consistent log message format.
- `create_log_folder()`: Creates the log folder specified in the `LOG_FOLDER`
  environment variable if it does not already exist, defaulting to `logs`.

Environment Variables:
- `LOG_LEVEL`: The logging level (e.g., DEBUG, INFO, WARNING, ERROR).
- `LOG_FOLDER`: The folder where log files will be stored.
- `dotenv`: Environment variables are loaded from a `.env` file.

Log Format:
The log messages are formatted as:
    `%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] - %(message)s`

Features:
- Rotating log files to manage disk usage (`maxBytes=10240`, `backupCount=5`).
- Configurable logging levels for different environments.
- Centralized log formatting for both file and stream handlers.

Usage:
Import and call the appropriate setup functions during the application 
initialization to enable logging.

Example:
    from logging_setup import setup_file_handler, setup_stream_handler, create_log_folder
    create_log_folder()
    app.logger.addHandler(setup_file_handler())
    app.logger.addHandler(setup_stream_handler())
"""


import logging
import os

from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()

# Set up logging
log_formatter = logging.Formatter(
    "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] - %(message)s"
)


def set_log_level():
    """
    Setup logging.
    """

    # get the log level from the environment, default to INFO
    log_level_env = os.getenv("LOG_LEVEL", "INFO")
    print(f"Info: log level set to {log_level_env}")
    if log_level_env == "DEBUG":
        log_level = logging.DEBUG
    elif log_level_env == "INFO":
        log_level = logging.INFO
    elif log_level_env == "WARNING":
        log_level = logging.WARNING
    elif log_level_env == "ERROR":
        log_level = logging.ERROR

    return log_level


def setup_file_handler():
    """
    Setup file handler.
    """
    # get log level
    log_level = set_log_level()
    # Create a file handler and set the formatter
    log_file = os.path.join(os.getenv("LOG_FOLDER"), "app.log")
    file_handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=5)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(log_formatter)
    return file_handler


def setup_stream_handler():
    """
    Setup stream handler.
    """
    # Create a stream handler and set the formatter
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    return stream_handler


def create_log_folder():
    """
    Create log folder from env variable LOG_FOLDER if it does not exist.
    if log folder does not exist, create it
    if env variable LOG_FOLDER is not set, use the default log folder
    """
    log_folder = os.getenv("LOG_FOLDER", "logs")
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
        print(f"Info: log folder {log_folder} created")
    else:
        print(f"Info: log folder {log_folder} exists")
    return
