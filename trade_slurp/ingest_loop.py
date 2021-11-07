import asyncio
import os
import time
import datetime
import json
import logging

import httpx
import poe_lib
import pymongo
import re



async def ingest():

    player_leagues_regex = re.compile(r'(PL[0-9]+)')

    mongo = pymongo.MongoClient(os.environ['MONGO_URL'])
    next_change_id = mongo.trade.config.find_one({'name': 'trade_slurper'})
    if next_change_id is not None:
        next_change_id = next_change_id['settings']['next_change_id']
    api = poe_lib.api.API()
    log = logging.getLogger('trade_slurp.ingest')


    print('\nBuild sold_items indexes.')
    print('├ Create Index [id: hashed]')
    mongo.trade.sold_items.create_index([('id', 'hashed')])
    print('├ Create Index [_soldOn]')
    mongo.trade.sold_items.create_index('_soldOn')
    print('├ Create Index [_price]')
    mongo.trade.sold_items.create_index('_price.unit')
    mongo.trade.sold_items.create_index('_price.value')
    mongo.trade.sold_items.create_index('_price.type')
    print('├ Create Index [extended.category]')
    mongo.trade.sold_items.create_index('extended.category')
    print('└ Create Index [typeLine]')
    mongo.trade.sold_items.create_index('typeLine')

    print('\nBuild item indexes.')
    print('├ Create Index [id hashed]')
    mongo.trade.items.create_index([('id', 'hashed')])
    print('├ Create Index [league]')
    mongo.trade.items.create_index('league')
    print('├ Create Index [_stash_id: hashed]')
    mongo.trade.items.create_index([('_stash_id', 'hashed')])
    print('├ Create Index [extended.category]')
    mongo.trade.items.create_index('extended.category')
    print('├ Create Index [extended.subcategories]')
    mongo.trade.items.create_index('extended.subcategories')
    # print('├ Create Index [note]')
    # mongo.trade.items.create_index('note')
    print('├ Create Index [_price]')
    mongo.trade.items.create_index('_price.unit')
    mongo.trade.items.create_index('_price.value')
    mongo.trade.items.create_index('_price.type')
    print('└ Create Index [typeLine]')
    mongo.trade.items.create_index('typeLine')

    print('\nBuild stash indexes.')
    print('├ Create Index [id]')
    mongo.trade.stashes.create_index('id')
    print('├ Create Index [_updatedOn]')
    mongo.trade.stashes.create_index('_updatedOn')
    print('├ Create Index [_insertedOn]')
    mongo.trade.stashes.create_index('_insertedOn')
    print('├ Create Index [accountName]')
    mongo.trade.stashes.create_index('accountName')
    print('├ Create Index [league]')
    mongo.trade.stashes.create_index('league')
    print('└ Create Index [_item_ids]')
    mongo.trade.stashes.create_index('_item_ids')

    grand_total_stashes = 0
    grand_total_items = 0
    start_time = time.time()
    error_delay = 1
    print('\nBuild stash indexes.')
    while True:
        t1 = time.time()
        try:
            r = await api.public_stash_tabs(next_change_id)
        except httpx.HTTPError as e:
            print(e)
            print(f'\nGot a status error [{e}] [{type(e)}], wait [{error_delay:.0f}] seconds.\n')
            await asyncio.sleep(error_delay)
            error_delay *= 1.5
            continue

        error_delay = 1
        next_change_id = r['next_change_id']
        total_items = 0
        total_stashes = 0
        bulk_item_operations = []
        bulk_stash_operations = []
        for stash in r['stashes']:

            if player_leagues_regex.search(str(stash['league'])):
                continue

            if stash['league'] is None:
                stash['league'] = "None"
            stash['league'] = stash['league'].replace('(', '_')
            stash['league'] = stash['league'].replace(')', '_')
            stash['league'] = stash['league'].replace(' ', '_')

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
                item_note = poe_lib.objects.Note(item.get('note', None))
                stash_note = poe_lib.objects.Note(stash.get('stash', None))

                if item_note.is_valid:
                    item['_price'] = {
                        'type': item_note.type,
                        'unit': item_note.unit,
                        'value': item_note.value,
                    }
                    bulk_item_operations.append(pymongo.ReplaceOne({'id': item['id']}, item, upsert=True))
                elif stash_note.is_valid:
                    item['_price'] = {
                        'type': stash_note.type,
                        'unit': stash_note.unit,
                        'value': stash_note.value,
                    }
                    bulk_item_operations.append(pymongo.ReplaceOne({'id': item['id']}, item, upsert=True))
                else:
                    items_to_forget.append(item['id'])


            stash['_item_ids'] = [item['id'] for item in stash['items'] if item['id'] not in items_to_forget]
            del stash['items']

            if len(stash['_item_ids']) > 0:
                bulk_stash_operations.append(pymongo.UpdateOne(
                    {'id': stash['id']},
                    {
                        '$set': {
                            **stash,
                            '_updatedOn': datetime.datetime.utcnow()
                        },
                        '$setOnInsert': {
                            '_insertedOn': datetime.datetime.utcnow()
                        }
                    },
                    upsert=True)
                )

        if len(bulk_item_operations):
            mongo.trade.items.bulk_write(bulk_item_operations, ordered=False)
        if len(bulk_stash_operations):
            mongo.trade.stashes.bulk_write(bulk_stash_operations, ordered=False)

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
        await asyncio.sleep(0)
        t2 = time.time()
        # print('Current Change ID:', next_change_id)
        # print('Grand Totals:')
        # print(f'   Stashes: {grand_total_stashes:13,}')
        # print(f'     Items: {grand_total_items:13,}')
        # print('Net Processing Rate:')
        # print(f' Stashes/s: {grand_total_stashes/(t2-start_time):12,.1f}')
        # print(f'   Items/s: {grand_total_items/(t2-start_time):12,.1f}')
        # print(f'Total processing time: {t2-t1:.1f} seconds.')
        # print(f'{total_items:,} items over {total_stashes:,} stashes.')
        # print(f'Ingest rate of {total_stashes/(t2-t1):10.1f} stashes/s.')
        # print(f'Ingest rate of {total_items/(t2-t1):10.1f} items/s.')
        # print()


        for n, value in enumerate([int(x) for x in next_change_id.split('-')]):
            poe_lib.Influx.write('trade_api', 'slurp', {'next_change_id': value}, {'shard': n+1, 'source': 'local'})

        poe_lib.Influx.write('trade_api', 'ingests', {'items': total_items, 'stashes': total_stashes})

        mongo_total_stashes = mongo.trade.stashes.estimated_document_count()
        mongo_total_items = mongo.trade.items.estimated_document_count()

        poe_lib.Influx.write(
            'trade_api',
            'metrics',
            {
                'duration_ingest': t2 - t1,
                'uptime': (t2 - start_time),
                'mongo_total_stashes': mongo_total_stashes,
                'mongo_total_items': mongo_total_items,
            }
        )

        # await asyncio.sleep(0.5)
