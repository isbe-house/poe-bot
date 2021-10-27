import asyncio
import os
import time
import datetime

import httpx
import poe_lib
import pymongo

async def main():
    mongo = pymongo.MongoClient(os.environ['MONGO_URL'])
    next_change_id = mongo.trade.config.find_one({'name': 'trade_slurper'})
    if next_change_id is not None:
        next_change_id = next_change_id['settings']['next_change_id']
    api = poe_lib.api.API(None)

    mongo.trade.items.create_index([('id', 1)])
    mongo.trade.stashes.create_index([('id', 1)])
    mongo.trade.stashes.create_index(
        'last_update',
        expireAfterSeconds=int(datetime.timedelta(days=14).total_seconds())
    )

    grand_total_stashes = 0
    grand_total_items = 0
    start_time = time.time()
    while True:
        t1 = time.time()
        try:
            r = await api.public_stash_tabs(next_change_id)
        except (httpx.HTTPStatusError, httpx.ReadTimeout):
            print('\nGot a status error, wait 60 seconds.\n')
            await asyncio.sleep(60)
            continue
        next_change_id = r['next_change_id']
        total_items = 0
        total_stashes = 0
        bulk_item_operations = []
        bulk_stash_operations = []
        for stash in r['stashes']:
            total_stashes += 1
            grand_total_stashes += 1

            items_to_forget = []
            for item in stash['items']:
                total_items += 1
                grand_total_items += 1
                item['_stash_id'] = stash['id']
                for junk_key in ['icon', 'descrText', 'flavourText', 'prophexyText']:
                    if junk_key in item:
                        del item[junk_key]

                # Only insert items with notes in the item or stash.
                if 'note' not in item and 'note' not in stash:
                    items_to_forget.append(item['id'])
                else:
                    bulk_item_operations.append(pymongo.ReplaceOne({'id': item['id']},item, upsert=True))

            stash['_item_ids'] = [item['id'] for item in stash['items'] if item['id'] not in items_to_forget]
            del stash['items']
            stash['last_update'] = datetime.datetime.utcnow()

            if len(stash['_item_ids']) > 0:
                bulk_stash_operations.append(pymongo.ReplaceOne({'id': stash['id']},stash, upsert=True))

        if len(bulk_item_operations):
            mongo.trade.items.bulk_write(bulk_item_operations)
        if len(bulk_stash_operations):
            mongo.trade.stashes.bulk_write(bulk_stash_operations)

        mongo.trade.config.find_one_and_update(
            {'name': 'trade_slurper'},
            {
                '$set': {
                    'settings': {
                        'next_change_id': next_change_id
                    }
                }
            },
            upsert=True,
        )
        t2 = time.time()
        print('Current Change ID:', next_change_id)
        print('Grand Totals:')
        print(f'   Stashes: {grand_total_stashes:10,}')
        print(f'     Items: {grand_total_items:10,}')
        print('Net Processing Rate:')
        print(f' Stashes/s: {grand_total_stashes/(t2-start_time):12,.1f}')
        print(f'   Items/s: {grand_total_items/(t2-start_time):12,.1f}')
        print(f'Total processing time: {t2-t1:.1f} seconds.')
        print(f'{total_items:,} items over {total_stashes:,} stashes.')
        print(f'Ingest rate of {total_stashes/(t2-t1):10.1f} stashes/s.')
        print(f'Ingest rate of {total_items/(t2-t1):10.1f} items/s.')
        print()
        # time.sleep(max(0, 1 - (t2-t1)))

asyncio.run(main())