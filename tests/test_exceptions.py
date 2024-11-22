# -*- coding: utf-8 -*-
"""
This module contains tests for the TokenError exception.
"""

import pytest
from app.exceptions import TokenError


def test_token_error_initialization():
    """
    Test the initialization of TokenError with a message and status code.
    """
    message = "Invalid token"
    status_code = 401

    # Instantiate TokenError
    error = TokenError(message, status_code)

    # Assert the message and status code are set correctly
    assert str(error) == message
    assert error.status_code == status_code


def test_token_error_raised():
    """
    Test raising TokenError and catching it.
    """
    message = "Token expired"
    status_code = 403

    # Raise and catch TokenError
    with pytest.raises(TokenError) as exc_info:
        raise TokenError(message, status_code)

    # Assert the exception was raised with the correct attributes
    assert str(exc_info.value) == message
    assert exc_info.value.status_code == status_code
