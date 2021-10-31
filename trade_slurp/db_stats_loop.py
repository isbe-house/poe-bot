import asyncio
import os
import time
import datetime
import json

import httpx
import poe_lib
import pymongo


async def db_stats():

    mongo = pymongo.MongoClient(os.environ['MONGO_URL'])

    while True:
        await asyncio.sleep(60)
        t1 = time.time()
        leages = mongo.trade.stashes.distinct('league')

        for league in leages:

            mongo_total_stashes = mongo.trade.stashes.count({'league': league})
            mongo_total_items = mongo.trade.items.count({'league': league})


            poe_lib.Influx.write(
                'trade_api',
                'league_metrics',
                {
                    'mongo_total_stashes': mongo_total_stashes,
                    'mongo_total_items': mongo_total_items,
                },
                {
                    'league': league
                }
            )