from typing import Any, Optional

from ..mongo import Mongo
from ..influx import Influx
from .object_base_class import BasePOEObject

class Character(BasePOEObject):
    id: str = None
    name: str = None
    class_: str = None
    league: str = None
    level: int
    experience: int
    expired: 'Optional[bool]' = None
    deleted: 'Optional[bool]' = None
    current: 'Optional[bool]' = None
    equipment = None  # TODO: Make an object of this
    inventory = None  # TODO: Make an object of this
    jewels = None  # TODO: Make an object of this
    passives = None  # TODO: Make an object of this

    @property
    def _auto_map(self):
        return {
            'id': str,
            'name': str,
            'class': {'class_': str},
            'league': str,
            'level': int,
            'experience': int,
            'expired': bool,
            'deleted': bool,
            'current': bool,
            'equipment': None,
            'inventory': None,
            'jewels': None,
            'passives': None,
        }

    def save(self):
        client = Mongo.client
        data = {
            'id': self.id,
            'name': self.name,
            'class': self.class_,
            'league': self.league,
            'level': self.level,
            'experience': self.experience,
        }

        old_data = client.characters.characters.find_one_and_update(
            {'id': data['id']},
            {'$set': {**data}},
            upsert=True,
        )

        if (old_data is not None) and (self.experience == old_data['experience']):
            return

        print('influx_write')
        Influx.write(
            'characters',
            'stats',
            {
                'level': self.level,
                'experience': self.experience,
            },
            {
                'char_name': ''.join([i if ord(i) < 128 else '' for i in self.name]),
            },
        )