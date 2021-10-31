from datetime import datetime
from abc import ABC
from typing import Any, Dict, Optional
import warnings


class BasePOEObject(ABC):
    '''Abstract base of all common discord objects. All subclasses map directly to an actual API object.'''

    _auto_map: dict = None  # type: ignore

    def __init__(self, data: Optional[dict] = None):
        '''Base generic __init__ function.

        Arguments:
            data (dict): Discord compliant dict for the given object.
        '''
        if type(self) is BasePOEObject:
            raise NotImplementedError('You cannot instance BasePOEObject directly. Use a child object.')

        if data is not None and isinstance(data, dict):
            self.from_dict(data)

    def from_dict(self, data: dict) -> 'BasePOEObject':
        '''Parse an object from a dictionary and return it.'''
        self._auto_dict(data)
        return self

    def to_dict(self) -> dict:
        '''Convert object to dictionary suitable for API or other generic useage.'''
        raise NotImplementedError(f'{self.__class__.__name__} does not yet implement this function.')

    def _auto_dict(self, data: 'Dict[str, Any]') -> 'BasePOEObject':
        '''Attempt an automatic conversion of a dict to this objects type.'''
        if self._auto_map is None:
            raise NotImplementedError(f'_auto_map not defined for {self.__class__}.')

        for attribute_key, value in data.items():
            if attribute_key not in self._auto_map:
                warnings.warn(RuntimeWarning(f'Saw unexpected attribute key [{attribute_key}] in [{self.__class__}].'))
                setattr(self, attribute_key, value)
                continue
            function = self._auto_map[attribute_key]
            if (function is None) or (value is None):
                continue
            if isinstance(function, list):
                if len(function) != 1:
                    raise IndexError('Auto map has function list in excess of 1.')
                if not isinstance(value, list):
                    raise TypeError(f'Data from input dict [{attribute_key}:{value}] was not a list with list auto_mapped type [{function}].')
                setattr(self, attribute_key, list())
                target_list: list = getattr(self, attribute_key)
                for sub_value in value:
                    target_list.append(function[0](sub_value))
            elif isinstance(function, dict):
                func_key = next(iter(function))
                function = function[func_key]
                setattr(self, func_key, function(value))
            else:
                setattr(self, attribute_key, function(value))
        return self

    @staticmethod
    def _fromtimestamp_milliseconds(time_stamp):
        return datetime.fromtimestamp(time_stamp / 1000)
