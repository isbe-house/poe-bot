import pytest
from unittest import mock
import os


@pytest.fixture(autouse=True)
def mock_env_vars():
    with mock.patch.dict(
        os.environ,
        {
            "POE_CLIENT_ID": "test_client_id",
            "POE_CLIENT_SECRET": "test_client_secret",
        }):
        yield