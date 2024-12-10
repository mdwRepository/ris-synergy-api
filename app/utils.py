# -*- coding: utf-8 -*-
"""
Module: sentry_util.py

This module provides a utility function to determine whether Sentry is enabled 
based on the presence of the `SENTRY_DSN` environment variable.

Function:
- `is_sentry_enabled()`:
  Checks if the `SENTRY_DSN` environment variable is set and returns a boolean 
  indicating whether Sentry integration is enabled.

  Returns:
    - `True`: If the `SENTRY_DSN` environment variable is set.
    - `False`: If the `SENTRY_DSN` environment variable is not set.

Environment Variables:
- `SENTRY_DSN`: The Data Source Name for Sentry. If this variable is set, it is 
  assumed that Sentry integration is enabled.

Usage:
This function is useful for conditionally enabling Sentry in an application based 
on the environment configuration.

Example:
    from sentry_util import is_sentry_enabled

    if is_sentry_enabled():
        import sentry_sdk
        sentry_sdk.init(
            dsn=os.getenv("SENTRY_DSN"),
            traces_sample_rate=1.0,
        )
        print("Sentry enabled")
    else:
        print("Sentry not enabled")
"""


import os

# Sentry utility function
def is_sentry_enabled():
    """
    Check if Sentry is enabled by verifying the presence of the SENTRY_DSN environment variable.
    """
    return bool(os.getenv("SENTRY_DSN"))
