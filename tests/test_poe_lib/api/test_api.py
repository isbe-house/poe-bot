from unittest import mock
from unittest.mock import patch, MagicMock
from ..fixtures import mock_httpx_async
import pytest


@pytest.mark.asyncio
async def test_basic(mock_httpx_async):
    mock_httpx_async.return_value.get.return_value.json.side_effect = [{"characters":[{"here": "there"}]}]
    from poe_lib.api import API

    x = API()
    with pytest.warns(RuntimeWarning):
        print('RETURNED:', await x.get_characters())