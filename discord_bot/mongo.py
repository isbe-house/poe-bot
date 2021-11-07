import pymongo
import motor.motor_asyncio
import os
from collections import defaultdict

from typing import Optional

class Mongo:

    @classmethod
    def defaulter(cls, input_dict: Optional[dict] = None):
        '''Validate the input dict was not None, and then return it as a defaulted dict.'''

        if input_dict is None:
            raise ValueError('No item found.')
        new_dict = defaultdict(lambda: None)
        new_dict.update(input_dict)
        return new_dict

    @classmethod
    @property
    def client(cls):
        return pymongo.MongoClient(os.environ['MONGO_URL'])

    @classmethod
    @property
    def async_client(cls):
        return motor.motor_asyncio.AsyncIOMotorClient(os.environ['MONGO_URL'])