import pytest
import pymongo
import os


@pytest.fixture
def mongo_client():
    client = pymongo.MongoClient(os.environ['MONGO_URL'])

    for db in client.list_databases():
        if db['name'] in ['admin', 'config', 'local']: continue
        client.drop_database(db['name'])

    yield client
