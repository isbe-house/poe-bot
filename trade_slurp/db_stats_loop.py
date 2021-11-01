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

    last_ninja_update = datetime.datetime.now() - datetime.timedelta(minutes = 5)

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

        if datetime.datetime.now() - last_ninja_update > datetime.timedelta(minutes = 5):
            last_ninja_update = datetime.datetime.now()
            try:
                r = httpx.get('https://poe.ninja/api/Data/GetStats')
                next_change_id = r.json()['next_change_id']
                print()
                for n, value in enumerate([int(x) for x in next_change_id.split('-')]):
                    poe_lib.Influx.write('trade_api', 'slurp', {'next_change_id': value}, {'shard': n+1, 'source': 'poe_ninja'})
            except Exception as e:
                print(f'Pulling poe-ninja got excxeption {e}')
                pass