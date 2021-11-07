import asyncio
import poe_lib
import os
import logging

from .ingest_loop import ingest
from .cleanup_loop import cleanup
from .db_stats_loop import db_stats
from .character_loop import character

async def main():

    with open('/run/secrets/client_id') as fp:
        os.environ['POE_CLIENT_ID'] = fp.read()

    with open('/run/secrets/client_token') as fp:
        os.environ['POE_CLIENT_TOKEN'] = fp.read()

    log = logging.getLogger('trade_slurp')
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('{asctime} [{levelname}] {funcName}:{levelno} {message}', style='{')
    ch.setFormatter(formatter)
    log.addHandler(ch)

    logging.getLogger('trade_slurp.character').setLevel(logging.DEBUG)
    logging.getLogger('trade_slurp.cleanup').setLevel(logging.ERROR)
    logging.getLogger('trade_slurp.ingest').setLevel(logging.ERROR)
    logging.getLogger('trade_slurp.db_stats').setLevel(logging.ERROR)

    # logging.getLogger('poe_lib').setLevel(1)

    base_coros = {
        'cleanup_task': cleanup,
        'ingest_task': ingest,
        'db_stats_task': db_stats,
        'character_task': character,
    }

    tasks = {
        'character_task': asyncio.create_task(character(), name='character_task'),
        'cleanup_task': asyncio.create_task(cleanup(), name='cleanup_task'),
        'ingest_task': asyncio.create_task(ingest(), name='ingest_task'),
        'db_stats_task': asyncio.create_task(db_stats(), name='db_stats_task'),
    }

    while True:

        await asyncio.sleep(5)

        for task_key, task in tasks.items():
            if task.done():
                log.critical(f'Found a done task: {task_key}')
                if task.exception():
                    try:
                        raise task.exception()  # type: ignore
                    except KeyboardInterrupt:
                        raise
                    except Exception:
                        log.exception(f'Got exception from {task}')
                        tasks[task_key] = await asyncio.create_task(base_coros[task_key]())

asyncio.run(main())