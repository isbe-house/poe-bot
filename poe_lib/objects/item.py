

from .object_base_class import BasePOEObject

class Item(BasePOEObject):

    @property
    def _auto_map(self):
        return {}