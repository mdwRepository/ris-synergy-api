# -*- coding: utf-8 -*-
"""
Module: exceptions.py

This module defines custom exceptions for the Flask application. These 
exceptions are used to handle specific application-level errors in a structured 
and consistent manner.

Classes:
- `TokenError`: Represents an error related to token validation or authentication.
  This exception includes a message describing the error and an associated HTTP 
  status code.

Usage:
Raise `TokenError` in cases where token validation fails, specifying an error 
message and the HTTP status code to be returned to the client.

Example:
    raise TokenError("Invalid token", 401)

Attributes:
- `message`: A description of the error.
- `status_code`: The HTTP status code to be returned in the response.

This module is designed to work seamlessly with Flask and can be integrated into
error handling mechanisms.
"""


class TokenError(Exception):
    """
    Exception raised for token validation errors.
    """

    def __init__(self, message, status_code):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        # Define custom attributes for the exception
        # the status code to be returned in the response
        self.status_code = status_code
