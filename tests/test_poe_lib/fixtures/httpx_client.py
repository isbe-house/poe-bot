from unittest.mock import patch, Mock, sentinel
import datetime
import pytest

@pytest.fixture
def mock_httpx_get():
    with patch('httpx.get') as method_mock:
        yield method_mock

@pytest.fixture
def mock_httpx_post():
    with patch('httpx.post') as method_mock:
        yield method_mock

@pytest.fixture
def mock_httpx_async():
    with patch('httpx.AsyncClient.__aenter__', spec=True) as mock:
        mock.return_value.patch.return_value.raise_for_status = Mock()
        mock.return_value.patch.return_value.headers = dict(
            {
                'x-ratelimit-reset': datetime.datetime.now().timestamp(),
                'x-ratelimit-remaining': 1,
            }
        )
        mock.return_value.patch.return_value.json = Mock(return_value=sentinel.JSON_RETURN)
        mock.return_value.patch.return_value.raise_for_status = Mock()

        mock.return_value.delete.return_value.raise_for_status = Mock()
        mock.return_value.delete.return_value.headers = dict(
            {
                'x-ratelimit-reset': datetime.datetime.now().timestamp(),
                'x-ratelimit-remaining': 1,
            }
        )
        mock.return_value.delete.return_value.json = Mock(return_value=sentinel.JSON_RETURN)

        mock.return_value.post.return_value.raise_for_status = Mock()
        mock.return_value.post.return_value.headers = dict(
            {
                'x-ratelimit-reset': datetime.datetime.now().timestamp(),
                'x-ratelimit-remaining': 1,
            }
        )
        mock.return_value.post.return_value.json = Mock(return_value=sentinel.JSON_RETURN)

        mock.return_value.get.return_value.raise_for_status = Mock()
        mock.return_value.get.return_value.headers = dict(
            {
                'x-ratelimit-reset': datetime.datetime.now().timestamp(),
                'x-ratelimit-remaining': 1,
            }
        )
        mock.return_value.get.return_value.json = Mock(return_value=sentinel.JSON_RETURN)
        yield mock