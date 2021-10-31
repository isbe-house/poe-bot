from .fixtures import mongo_client


def test_fixture(mongo_client):
    print(mongo_client)

    mongo_client.test1.test.insert_one({'test': 'doc'})

    for db in mongo_client.list_databases():
        print(db)


def test_fixture2(mongo_client):
    print(mongo_client)

    mongo_client.test2.test.insert_one({'test': 'doc'})

    for db in mongo_client.list_databases():
        print(db)