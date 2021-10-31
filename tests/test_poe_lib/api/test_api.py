from unittest import mock
from unittest.mock import patch, MagicMock
from ..fixtures import mock_httpx_get

def test_basic(mock_httpx_get):
    from poe_lib.api import API

    mock_httpx_get.return_value.json.side_effect = ['FOO']

    x = API()
    print('RETURNED:', x.get_characters())