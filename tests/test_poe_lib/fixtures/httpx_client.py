from unittest.mock import patch, Mock

import pytest

@pytest.fixture
def mock_httpx_get():
    with patch('httpx.get') as method_mock:
        yield method_mock

@pytest.fixture
def mock_httpx_post():
    with patch('httpx.post') as method_mock:
        yield method_mock
