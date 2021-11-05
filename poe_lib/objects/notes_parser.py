
import re
import enum
from typing import Optional


class Note:

    CURRENCY_MATCHER = re.compile(r'[~-]?(b/[o0]|price)\s?(\d+(?:\.\d*)?(?:/\d+(?:\.\d*)?)?)\s([a-zA-Z-]+)')

    CURRENCY_REMAP = {
        'alch': 'Orb of Alchemy',
        'alt': 'Orb of Alteration',
        'armour': 'Armourer\'s Scrap',
        'awakened-sextant': 'Awakened Sextant',
        'bauble': 'Glassblower\'s Bauble',
        'blessed': 'Blessed Orb',
        'cart': 'Cartographer\'s Chisel',
        'chanc': 'Orb of Chance',
        'chance': 'Orb of Chance',
        'chaos': 'Chaos Orb',
        'Chaos': 'Chaos Orb',
        'CHAOS': 'Chaos Orb',
        'chaos-orb': 'Chaos Orb',
        'chisel': 'Cartographer\'s Chisel',
        'chrom': 'Chromatic Orb',
        'chrome': 'Chromatic Orb',
        'div': 'Divine Orb',
        'divine': 'Divine Orb',
        'ex': 'Exalted Orb',
        'exa': 'Exalted Orb',
        'exalt': 'Exalted Orb',
        'exalted orb': 'Exalted Orb',
        'exalted-orb': 'Exalted Orb',
        'exalted': 'Exalted Orb',
        'Exalted': 'Exalted Orb',
        'fusing': 'Orb of Fusing',
        'gcp': 'Gemcutter\'s Prism',
        'jewellers': 'Jeweller\'s Orb',
        'kalandra': 'Mirror of Kalandra',
        'mir': 'Mirror of Kalandra',
        'mirror': 'Mirror of Kalandra',
        'regal': 'Regal Orb',
        'regret': 'Orb of Regret',
        'scour': 'Orb of Scouring',
        'silver': 'Silver Coin',
        'vaal': 'Vaal Orb',
        'whetstone': 'Blacksmith\'s Whetstone',
        'aug': 'Orb of Augmentation',
        'engineers': 'Engineer\'s Orb',
    }

    TYPE_REMAP = {
        'b/0': 'b/o'
    }

    def __init__(self, value_string: str = None):
        self.value_string = value_string
        self.type: str = None
        self.value: float = None
        self.unit: str = None
        self.is_valid = False

        if value_string is None:
            return

        match_obj = self.CURRENCY_MATCHER.search(value_string)

        if match_obj:
            try:
                self.value = eval(match_obj.group(2), {"__builtins__": None}, {"__builtins__": None})
            except (SyntaxError, ZeroDivisionError):
                return
            self.type = match_obj.group(1)
            self.unit = match_obj.group(3)

            if self.unit in self.CURRENCY_REMAP:
                self.unit = self.CURRENCY_REMAP[self.unit]

            if self.type in self.TYPE_REMAP:
                self.type = self.TYPE_REMAP[self.type]

            if not isinstance(self.value, (int, float)):
                return

            if self.value > 0:
                self.is_valid = True
