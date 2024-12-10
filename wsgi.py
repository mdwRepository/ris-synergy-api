# -*- coding: utf-8 -*-
"""
Module: wsgi.py

This module serves as the entry point for running the Flask application using 
a WSGI server. It imports the Flask app instance from the `app` module and 
executes it in standalone mode if run directly.

Features:
- Imports the initialized Flask application from the `app` module.
- Provides a `__main__` block to run the app using Flask's built-in server.

Usage:
This file is commonly used in production with a WSGI server such as Gunicorn or uWSGI. 
For example:
    gunicorn wsgi:app

Direct Execution:
The app can also be started using Flask's built-in development server by running:
    python wsgi.py

Notes:
- The built-in server is not suitable for production and should only be used 
  for local development.
- Ensure the app is properly configured for production when using a WSGI server.

Example:
    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)
"""


from app import app

if __name__ == "__main__":
    app.run()
