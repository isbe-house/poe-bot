import asyncio
import os
import time
import datetime

import httpx
import poe_lib
import pymongo
import re

from .mongo import mongo_async_client

async def cleanup():

    MAX_ALLOWED_STASH_AGE = datetime.timedelta(days=3)
    player_leagues_regex_string = r'(PL[0-9]+)'

    mongo = pymongo.MongoClient(os.environ['MONGO_URL'])

    mongo_client = await mongo_async_client()

    while True:


        t_start = time.time()

        stash_update_config = await mongo_client.trade.config.find_one({'name': 'cleanup'})
        if stash_update_config is None:
            stash_update_config = {
                'name': 'cleanup',
                'settings': {
                    'stash_update_cursor': datetime.datetime.min,
                }
            }
            await mongo_client.trade.config.insert_one(stash_update_config)

        t_config_load = time.time()

        # Cleanup bad entries
        items_for_deletion = []
        sold_items_for_deletion = []
        stashes_for_deletion = []

        # print('Searching for Invalid Stashes...')
        filter = {'_updatedOn': None}
        async for stash in mongo_client.trade.stashes.find(filter=filter).sort('_updatedOn'):
            stashes_for_deletion.append(pymongo.DeleteOne({'id': stash['id']}))
            items_for_deletion.append(pymongo.DeleteMany({'_stash_id': stash['id']}))

            if len(stashes_for_deletion) >= 1e5:
                # print('Found lots of things, just delete and move on.')
                break

        filter = {'league': {'$regex': player_leagues_regex_string}}
        async for stash in mongo_client.trade.stashes.find(filter=filter):
            stashes_for_deletion.append(pymongo.DeleteOne({'id': stash['id']}))
            items_for_deletion.append(pymongo.DeleteMany({'_stash_id': stash['id']}))

            if len(stashes_for_deletion) >= 1e5:
                # print('Found lots of things, just delete and move on.')
                break

        await asyncio.sleep(0)

        # print('Searching for invalid Sales...')
        filter = {'_soldOn': None}
        async for item in mongo_client.trade.sold_items.find(filter=filter):
            sold_items_for_deletion.append(pymongo.DeleteOne({'id': item['id']}))

            if len(sold_items_for_deletion) >= 1e4:
                # print('Found lots of things, just delete and move on.')
                break

        await asyncio.sleep(0)

        if len(items_for_deletion):
            # print(f'Deleting {len(items_for_deletion):,d} invalid items...')
            await mongo_client.trade.items.bulk_write(items_for_deletion, ordered=False)
        await asyncio.sleep(0)
        if len(sold_items_for_deletion):
            # print(f'Deleting {len(sold_items_for_deletion):,d} invalid sold items...')
            await mongo_client.trade.sold_items.bulk_write(sold_items_for_deletion, ordered=False)
        await asyncio.sleep(0)
        if len(stashes_for_deletion):
            # print(f'Deleting {len(stashes_for_deletion):,d} invalid stashes...')
            await mongo_client.trade.stashes.bulk_write(stashes_for_deletion, ordered=False)

        await asyncio.sleep(0)

        t_start_age_off = time.time()
        # Age off old stashes, delete any items within them.
        filter = {'_updatedOn': {'$lte': datetime.datetime.utcnow() - MAX_ALLOWED_STASH_AGE}}

        items_for_deletion = []
        stashes_for_deletion = []
        async for stash in mongo_client.trade.stashes.find(filter=filter).sort('_updatedOn'):
            if datetime.datetime.utcnow() - stash['_updatedOn'] > MAX_ALLOWED_STASH_AGE:
                stashes_for_deletion.append(pymongo.DeleteOne({'id': stash['id']}))
                items_for_deletion.append(pymongo.DeleteMany({'_stash_id': stash['id']}))
            else:
                break

        await asyncio.sleep(0)

        if len(items_for_deletion):
            await mongo_client.trade.items.bulk_write(items_for_deletion, ordered=False)
        await asyncio.sleep(0)
        if len(stashes_for_deletion):
            await mongo_client.trade.stashes.bulk_write(stashes_for_deletion, ordered=False)
        t_end_age_off = time.time()
        await asyncio.sleep(0)

        last_cursor_update = datetime.datetime.utcnow()

        filter = {'_updatedOn': {'$gte': stash_update_config['settings']['stash_update_cursor']}}

        sold_item_counter = 0

        t_start_sell_items = time.time()
        bulk_items_sold_write_queue = []
        bulk_items_write_queue = []
        async for stash in mongo_client.trade.stashes.find(filter=filter).sort('_updatedOn'):
            async for item in mongo_client.trade.items.find({'_stash_id': stash['id']}, projection={'_id': 0}):
                if item['id'] not in stash['_item_ids']:
                    if 'note' not in item or item['note'] is None:
                        item['note'] = stash['note']
                    sold_item_counter += 1
                    update_op = pymongo.UpdateOne(
                        {'id': item['id']},
                        {
                            '$set': {
                                **item,
                            },
                            '$setOnInsert': {
                                '_soldOn': datetime.datetime.utcnow()
                            },
                        },
                        upsert=True
                    )
                    delete_op = pymongo.DeleteOne({'id': item['id']})
                    bulk_items_sold_write_queue.append(update_op)
                    bulk_items_write_queue.append(delete_op)
            if len(bulk_items_sold_write_queue):
                await mongo_client.trade.sold_items.bulk_write(bulk_items_sold_write_queue, ordered=False)
                bulk_items_sold_write_queue = []
            if len(bulk_items_write_queue):
                await mongo_client.trade.items.bulk_write(bulk_items_write_queue, ordered=False)
                bulk_items_write_queue = []
            behind = datetime.datetime.utcnow() - stash['_updatedOn']

            await asyncio.sleep(stash_update_config['settings']['artifical_delay'])

            if datetime.datetime.utcnow() > last_cursor_update + datetime.timedelta(minutes = 1):
                if behind > datetime.timedelta(minutes = 10):
                    print(f'\nCleanup is currently [{behind}] behind!')
                last_cursor_update = datetime.datetime.utcnow()
                break

        await mongo_client.trade.config.find_one_and_update({'name': 'cleanup'},{'$set': {'settings.stash_update_cursor': stash['_updatedOn']}}, upsert=True)

        t_end_sell_items = time.time()
        poe_lib.Influx.write(
            'trade_api',
            'ingests',
            {
                'items_sold': sold_item_counter,
            }
        )
        poe_lib.Influx.write(
            'trade_api',
            'metrics',
            {
                'duration_total_cleanup_loop': t_end_sell_items - t_start,
                'duration_config_cleanup': t_config_load - t_start,
                'duration_contigency_cleanup': t_start_age_off - t_config_load,
                'duration_age_off_cleanup': t_end_age_off - t_start_age_off,
                'duration_sell_items_cleanup': t_end_sell_items - t_start_sell_items,
                'cleanup_lag': behind.total_seconds(),
            }
        )

        if behind < datetime.timedelta(minutes = 5):
            await asyncio.sleep(60)
