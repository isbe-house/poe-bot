import asyncio
import os
import time
import datetime

import httpx
import poe_lib
import pymongo

mongo = pymongo.MongoClient(os.environ['MONGO_URL'])

pipeline = [
    {
        '$lookup': {
            'from': 'stashes',
            'localField': '_stash_id',
            'foreignField': 'id',
            'as': 'orphans'
        }
    },
    {
        '$match': { 'orphans': [] }
    }
]

items_for_deletion = []
for item in mongo.trade.items.aggregate(pipeline):
    items_for_deletion.append(pymongo.DeleteOne({'_id': item['_id']}))

    if len(items_for_deletion) >= 1024:
        print('DELETE')
        mongo.trade.items.bulk_write(items_for_deletion, ordered=False)
        items_for_deletion = []

if len(items_for_deletion):
    mongo.trade.items.bulk_write(items_for_deletion, ordered=False)
