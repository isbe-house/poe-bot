from typing import Any, Optional

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
