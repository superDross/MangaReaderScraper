"""
Functions to aid unit testing
"""

from unittest import mock


def mock_requests_get_return(contents):
    requests_return = mock.MagicMock()
    requests_return.content = contents
    requests_return.text.read = mock.MagicMock(return_value=contents)
    return requests_return
