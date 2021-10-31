from unittest.mock import patch, Mock

import pytest

@pytest.fixture
def mock_poe_api():
    with patch('poe_lib.api.API') as class_mock:
        # mock.get_user = AsyncMock(return_value=samples.dev_user)
        # mock.get_channel = AsyncMock(return_value=channel_samples.dev_guild_text)
        # mock.get_guild_roles = AsyncMock(return_value=[role_samples.dev_role])
        class_mock.return_value.refresh_token.return_value = Mock(
            return_value={
                "access_token": "41bcefbc2f0d6ea0fa1cce10c435310d3c475e5b",
                "expires_in": 2592000,
                "token_type": "bearer",
                "scope": "account:profile account:stashes"
            }
        )
        class_mock.return_value.client_id = 'test_client_id'
        class_mock.return_value.client_secret = 'test_client_secret'
        yield class_mock
