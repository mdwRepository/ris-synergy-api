# -*- coding: utf-8 -*-

import logging
import os

from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

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
