from unittest.mock import sentinel
import pytest
from datetime import datetime, timedelta

from poe_lib import Account, SCOPES

from ..fixtures import mongo_client, mock_poe_api, mock_httpx_get, mock_httpx_post

def test_basic():
    x = Account()

    assert isinstance(x, Account)

def test_magics():
    obj = Account(sentinel.DISCORD_ID)

    assert obj.discord_user_id == sentinel.DISCORD_ID

def test_sopes():

    for scope in SCOPES:
        print(scope)

def test_saving(mongo_client):
    assert mongo_client.accounts.discord_accounts.find_one({'discord_user_id': 'test_id'}) is None

    obj = Account('test_id')
    obj.generate()
    obj.save(force=True)

    assert mongo_client.accounts.discord_accounts.find_one({'discord_user_id': 'test_id'}) is not None

    obj2 = Account('test_id')
    obj.load()

    assert obj2.discord_user_id == obj2.discord_user_id

def test_get_token(mock_poe_api, mock_httpx_get):

    mock_poe_api.return_value.get_token.return_value = {
        "access_token": "486132c90fedb152360bc0e1aa54eea155768eb9",
        "expires_in": 2592000,
        "token_type": "bearer",
        "scope": "account:profile",
        "refresh_token": "17abaa74e599192f7650a4b89b6e9dfef2ff68cd"
    }

    mock_poe_api.return_value.refresh_token.return_value = {
        "access_token": "41bcefbc2f0d6ea0fa1cce10c435310d3c475e5b",
        "expires_in": 2592000,
        "token_type": "bearer",
        "scope": "account:profile"
    }

    obj = Account('test discord id')
    obj.save(force=True)

    obj = Account('test discord id')
    obj.load()
    obj.generate()
    obj.get_access_token('12345')

    token = obj.bearer_token
    assert token is not None
    mock_poe_api.return_value.get_token.assert_called()
    mock_poe_api.return_value.refresh_token.assert_not_called()

def test_refresh_token(mock_poe_api, mock_httpx_get):

    mock_poe_api.return_value.get_token.return_value = {
        "access_token": "486132c90fedb152360bc0e1aa54eea155768eb9",
        "expires_in": 0,
        "token_type": "bearer",
        "scope": "account:profile",
        "refresh_token": "17abaa74e599192f7650a4b89b6e9dfef2ff68cd"
    }

    mock_poe_api.return_value.refresh_token.return_value = {
        "access_token": "41bcefbc2f0d6ea0fa1cce10c435310d3c475e5b",
        "expires_in": 2592000,
        "token_type": "bearer",
        "scope": "account:profile"
    }

    obj = Account('test discord id')
    obj.save(force=True)

    obj = Account('test discord id')
    obj.load()
    obj.generate()
    obj.get_access_token('12345')

    token = obj.bearer_token
    assert token is not None
    mock_poe_api.return_value.get_token.assert_called()
    mock_poe_api.return_value.refresh_token.assert_called()

def test_registration_flow(mock_poe_api, mongo_client):
    pass

def test_expired_access_token(mongo_client, mock_poe_api):

    mock_poe_api.return_value.get_token.return_value = {
        "access_token": "486132c90fedb152360bc0e1aa54eea155768eb9",
        "expires_in": 2592000,
        "token_type": "bearer",
        "scope": "account:profile",
        "refresh_token": "17abaa74e599192f7650a4b89b6e9dfef2ff68cd"
    }

    obj = Account('test discord id')
    obj.generate()
    obj.save(force=True)

    for account in mongo_client.accounts.discord_accounts.find():
        if account['discord_user_id'] == obj.discord_user_id:
            print(account)
            break
    else:
        assert False

    # Assume website calls next value

    new_obj = Account('test discord id')

    new_obj.load()
    new_obj.get_access_token('test code')

    assert new_obj.access_token_expiration is not None
    assert isinstance(new_obj.access_token_expiration, datetime)
    assert (new_obj.access_token_expiration - datetime.utcnow()) < timedelta(seconds = 2592000)

    assert new_obj.refresh_token_expiration is not None
    assert isinstance(new_obj.refresh_token_expiration, datetime)

    assert new_obj.token_type == 'bearer'
