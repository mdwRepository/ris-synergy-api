# -*- coding: utf-8 -*-
"""
Module: extensions.py

This module initializes and configures extensions for the Flask application. 
Currently, it is responsible for setting up Cross-Origin Resource Sharing (CORS) 
using Flask-CORS.

Components:
- `allowed_origins`: A list of allowed origins for CORS, read from the 
  `ALLOWED_ORIGINS` environment variable. Origins are separated by commas in the 
  environment variable.
- `cors`: An instance of Flask-CORS configured with the allowed origins.

Purpose:
CORS is used to enable resource sharing across different origins, making the 
application accessible from specified client origins while maintaining security.

Usage:
Import `cors` from this module and apply it to the Flask application during 
initialization to enable CORS functionality.

Dependencies:
- `flask_cors.CORS`: A Flask extension for handling CORS.

Environment Variables:
- `ALLOWED_ORIGINS`: Comma-separated list of origins allowed for CORS. Example:
  ALLOWED_ORIGINS="http://example.com,http://anotherdomain.com"

Example:
    from extensions import cors
    cors.init_app(app)
"""


import os

from flask_cors import CORS


# Read allowed origins from environment variable
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

# Allow CORS
cors = CORS(origins=allowed_origins)
