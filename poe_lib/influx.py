import httpx
from datetime import datetime
from typing import Any, Optional


class Influx:

    URL = "http://influx:8086"

    @classmethod
    def write(cls, db: 'str', measurement: 'str',  fields: 'dict[str, Any]', tags: 'Optional[dict[str, Any]]' = None, timestamp: 'Optional[datetime]' = None, precision: str = 's'):
        '''Writes to the database.'''

        if precision not in ('n', 'u', 'ms', 's', 'm', 'h'):
            raise ValueError(f'precision had invalid value [{precision}], must be in [n,u,ms,s,m,h]')

        line = f'{measurement}'
        if tags is not None:
            tag_string = ','.join([f'{k}={v}' for (k, v) in tags.items()])
            line += f',{tag_string}'
        line += ' '
        line += ','.join([f'{k}={v}' for (k, v) in fields.items()])

        if timestamp is not None:
            line += f' {timestamp.isoformat()}'

        httpx.post(
            url = cls.URL + '/write',
            params={'db': db},
            data=line,
        )
