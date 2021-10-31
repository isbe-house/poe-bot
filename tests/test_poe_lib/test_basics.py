
from .fixtures import mock_env_vars, mock_poe_api

def test_basic():
    from poe_lib.api import API
    x = API('1234')

    assert x is not None

    print(x.user_agent)


def test_environ1():
    import os

    assert 'FOO' not in os.environ
    os.environ['FOO'] = 'BAR'


def test_environ2():
    import os

    assert 'FOO' not in os.environ
    os.environ['FOO'] = 'BAR'

    assert os.environ['POE_CLIENT_ID'] == 'test_client_id'
    assert os.environ['POE_CLIENT_SECRET'] == 'test_client_secret'

def test_api_return(mock_env_vars, mock_poe_api):
    obj = mock_poe_api()
    assert obj.client_id == 'test_client_id'