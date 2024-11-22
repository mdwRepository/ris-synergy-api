# -*- coding: utf-8 -*-
"""
Module: template_filters.py

This module defines and registers custom Jinja2 template filters for a Flask 
application. These filters are designed to enhance template functionality by 
transforming data into more human-readable formats.

Functions:
- `register_template_filters(app)`: Registers all custom template filters with 
  the provided Flask application instance.
- `isoformat_to_human(value, format="%B %d, %Y %H:%M")`: Converts ISO 8601 
  formatted datetime strings into a more human-readable format, with an optional
  customizable output format.

Features:
- Handles ISO 8601 date parsing and formatting.
- Returns an empty string for `None` values to prevent display issues.
- Gracefully falls back to the original value if parsing fails.

Dependencies:
- `datetime`: For handling date and time parsing and formatting.
- `pytz`: For timezone handling, ensuring the datetime is correctly processed 
  in UTC or a specific timezone as needed.

Usage:
Call `register_template_filters(app)` during the Flask application setup process 
to make the custom filters available in Jinja2 templates.

Example:
    {{ some_iso_date_string|isoformat_to_human("%Y-%m-%d") }}

Default Format:
- The default format is `"%B %d, %Y %H:%M"`, which results in output like 
  "November 22, 2024 14:30".

Error Handling:
- If the input is not a valid ISO 8601 string, the filter returns the original 
  value without modifications.
"""


import datetime
import pytz


def register_template_filters(app):
    """
    Register custom template filters.
    """

    @app.template_filter("isoformat_to_human")
    def isoformat_to_human(value, date_format="%B %d, %Y %H:%M"):
        """
        Convert ISO format string to a more readable format for use in templates.
        """
        if value is None:
            return ""
        # Parse the ISO format string to datetime object
        try:
            # If your dates are always in UTC, ensure to convert them properly to the desired timezone here
            dt = datetime.datetime.fromisoformat(value.rstrip("Z")).replace(
                tzinfo=pytz.utc
            )
            # Convert to local time or another timezone if needed, e.g., dt.astimezone(pytz.timezone('Europe/Vienna'))
        except ValueError:
            return value  # Return the original value if parsing fails
        return dt.strftime(date_format)
