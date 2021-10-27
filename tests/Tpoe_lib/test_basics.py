from poe_lib.api import API

def test_basic():

    x = API('1234')

    assert x is not None

    print(x.user_agent)