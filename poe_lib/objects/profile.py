from typing import Any, Optional

from .object_base_class import BasePOEObject

class Character(BasePOEObject):
    uuid: str = None  # string  UUIDv4 in canonical format
    name: str = None  #  string
    realm: Optional[str] = None  #  ?string  pc, xbox, or sony
    guild: 'Optional[Guild]' = None  #  ?object  present if the account has a guild
    twitch: 'Optional[Twtich]' = None #  ?object  present if the account is Twitch-linked

    @property
    def _auto_map(self):
        return {
            'uuid': str,
            'name': str,
            'realm': str,
            'guild': Guild,
            'twtich': Twtich,
        }

class Guild(BasePOEObject):
    name: str = None

    @property
    def _auto_map(self):
        return {
            'name': str,
        }

class Twtich(BasePOEObject):
    name: str = None

    @property
    def _auto_map(self):
        return {
            'name': str,
        }
