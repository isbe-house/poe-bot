import pymongo
import os
from collections import defaultdict

from typing import Optional

class Mongo:

    _client: pymongo.MongoClient

    @classmethod
    def connect(cls):
        cls._client = pymongo.MongoClient(os.environ['MONGO_URL'])


    @classmethod
    @property
    def client(cls):
        if not hasattr(cls, "_client"):
            cls.connect()
        return cls._client
