from datetime import datetime
from typing import Any, Optional, List

from dateutil.parser import parse

from .object_base_class import BasePOEObject

class League(BasePOEObject):
    id: str = None
    realm: str = None
    description: str = None
    rules: 'List[LeagueRule]' = None
    registerAt: datetime = None
    event: bool = None
    url: str = None
    startAt: str = None
    endAt: str = None
    timedEvent: bool = None
    scoreEvent: bool = None
    delveEvent: bool = None

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.__str__()

    @property
    def _auto_map(self):
        return {
            'id': str,
            'realm': str,
            'description': str,
            'rules': [LeagueRule],
            'registerAt': parse,
            'event': bool,
            'url': str,
            'startAt': str,
            'endAt': str,
            'timedEvent': bool,
            'scoreEvent': bool,
            'delveEvent': bool,
        }

class LeagueRule(BasePOEObject):
    id: str = None
    name: str = None
    description: str = None

    @property
    def _auto_map(self):
        return {
            'id': str,
            'name': str,
            'description': str,
        }