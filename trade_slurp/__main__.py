import asyncio
import poe_lib
import os

from .ingest_loop import ingest
from .cleanup_loop import cleanup
from .db_stats_loop import db_stats

async def main():

    with open('/run/secrets/client_id') as fp:
        os.environ['POE_CLIENT_ID'] = fp.read()

    log = poe_lib.Log()

    base_coros = {
        'cleanup_task': cleanup,
        'ingest_task': ingest,
        'db_stats_task': db_stats,
    }

    tasks = {
        'cleanup_task': asyncio.create_task(cleanup(), name='cleanup_task'),
        'ingest_task': asyncio.create_task(ingest(), name='ingest_task'),
        'db_stats_task': asyncio.create_task(db_stats(), name='db_stats_task'),
    }

    while True:

        await asyncio.sleep(60)

        for task_key, task in tasks.items():
            if task.done():
                if task.exception():
                    try:
                        raise task.exception()
                    except KeyboardInterrupt:
                        raise
                    except Exception:
                        log.exception(f'Got exception from {task}')
                        tasks[task_key] = await asyncio.create_task(base_coros[task_key]())

asyncio.run(main())