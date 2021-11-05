from datetime import datetime
from typing import Any, Optional, List

from dateutil.parser import parse

from .object_base_class import BasePOEObject
from . import item as ext_item

class Stash(BasePOEObject):
    id: str = None  # type: ignore
    parent: str = None  # type: ignore
    name: str = None  # type: ignore
    type: str = None  # type: ignore
    index: int = None  # type: ignore
    metadata: 'StashMetadata' = None  # type: ignore
    children: 'List[Stash]' = None  # type: ignore
    items: 'List[ext_item.Item]' = None  # type: ignore

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    @property
    def _auto_map(self):
        return {
            'id': str,
            'parent': str,
            'name': str,
            'type': str,
            'index': int,
            'metadata': StashMetadata,
            'children': [Stash],
            'items': [ext_item.Item],
        }

class StashMetadata(BasePOEObject):
    public: bool = None
    folder: bool = None
    colour: str = None

    @property
    def _auto_map(self):
        return {
            'public': bool,
            'folder': bool,
            'colour': str,
        }