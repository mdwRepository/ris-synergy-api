# -*- coding: utf-8 -*-

import os

from flask_cors import CORS


# Read allowed origins from environment variable
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

# Allow CORS
cors = CORS(origins=allowed_origins)
