

from .object_base_class import BasePOEObject

class Item(BasePOEObject):
    verified: bool = None  # type: ignore
    w: int = None  # type: ignore
    h: int = None  # type: ignore
    icon: str = None  # type: ignore
    # support bool always true if present
    stackSize: int = 1  # Default to something sane.
    maxStackSize: int = None  # type: ignore
    stackSizeText: str = None  # type: ignore
    league: str = None  # type: ignore
    id: str = None  # type: ignore  a unique 64 digit hexadecimal str
    influences: object = None  # type: ignore
    elder: bool = None  # type: ignore  always true if present
    shaper: bool = None  # type: ignore  always true if present
    abyssJewel: bool = None  # type: ignore  always true if present
    delve: bool = None  # type: ignore  always true if present
    fractured: bool = None  # type: ignore  always true if present
    synthesised: bool = None  # type: ignore  always true if present
    # sockets array of ItemSocket
    # socketedItems array of Item
    name: str = None  # type: ignore
    typeLine: str = None  # type: ignore
    baseType: str = None  # type: ignore
    identified: bool = None  # type: ignore
    itemLevel: int = None  # type: ignore
    ilvl: int = None  # type: ignore deprecated
    note: str = None  # type: ignore
    forum_note: str = None  # type: ignore
    # lockedToCharacter bool always true if present
    # lockedToAccount bool always true if present
    # duplicated bool always true if present
    # split bool always true if present
    # corrupted bool always true if present
    # cisRaceReward bool always true if present
    # seaRaceReward bool always true if present
    # thRaceReward bool always true if present
    # properties array of ItemProperty
    # notableProperties array of ItemProperty
    # requirements array of ItemProperty
    # additionalProperties array of ItemProperty
    # nextLevelRequirements array of ItemProperty
    # talismanTier int
    # secDescrText str
    # utilityMods array of str
    # logbookMods array of object
    # ↳ name str area name
    # ↳ faction object
    #   ↳ id str Faction1, Faction2, Faction3, or Faction4
    #   ↳ name str
    # ↳ mods array of str
    # enchantMods array of str
    # scourgeMods array of str
    # implicitMods array of str
    # ultimatumMods array of object
    # ↳ type str text used to display ultimatum icons
    # ↳ tier uint
    # explicitMods array of str
    # craftedMods array of str
    # fracturedMods array of str
    # cosmeticMods array of str
    # veiledMods array of str random video identifier
    # veiled bool always true if present
    # descrText str
    # flavourText array of str
    # flavourTextParsed array of str
    # prophecyText str
    # isRelic bool always true if present
    # replica bool always true if present
    # incubatedItem object
    # ↳ name str
    # ↳ level uint monster level required to progress
    # ↳ progress uint
    # ↳ total uint
    # scourged object
    # ↳ tier uint 1-3 for items, 1-10 for maps
    # ↳ level uint monster level required to progress
    # ↳ progress uint
    # ↳ total uint
    # frameType uint
    # artFilename str
    # hybrid object
    # ↳ isVaalGem bool
    # ↳ baseTypeName str
    # ↳ properties array of ItemProperty
    # ↳ explicitMods array of str
    # ↳ secDescrText str
    # extended object only present in the Public Stash API
    # ↳ category str
    # ↳ subcategories array of str
    # ↳ prefixes uint
    # ↳ suffixes uint
    x: int = None  # type: ignore
    y: int = None  # type: ignore
    # inventoryId str
    # socket uint
    colour: str = None  # type: ignore S, D, I, or G
    @property
    def _auto_map(self):
        return {
            'league': str,
            'stackSize': int,
            'maxStackSize': int,
            'name': str,
            'typeLine': str,
            'baseType': str,
            'note': str,
        }

class ItemSocket:
    # group uint
    # attr str S, D, I, G, A, or DV
    # sColour str R, G, B, W, A, or DV
    pass

class ItemProperty:
    # name string
    # values array
    # ↳ 0 string
    # ↳ 1 uint value type
    # displayMode uint
    # progress ?double rounded to 2 decimal places
    # type ?uint
    # suffix ?string
    pass