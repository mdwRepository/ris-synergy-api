# -*- coding: utf-8 -*-

import datetime
import pytz


def register_template_filters(app):
    """
    Register custom template filters.
    """

    @app.template_filter("isoformat_to_human")
    def isoformat_to_human(value, format="%B %d, %Y %H:%M"):
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
        return dt.strftime(format)
