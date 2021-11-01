
import re

class Note:

    currency_matcher = re.compile('[~-]?(b\/o|price)\s?([\d\.\/ ]+)\s([a-zA-Z-]+)')

    def __init__(self, value_string: str = None):
        self.value_string = value_string
        self.type: str = None
        self.value: float = None
        self.unit: str = None
        self.is_valid = False

        match_obj = self.currency_matcher.search(value_string)

        if match_obj:
            try:
                self.value = eval(match_obj.group(2), {"__builtins__": None}, {"__builtins__": None})
            except (SyntaxError, ZeroDivisionError):
                return
            self.type = match_obj.group(1)
            self.unit = match_obj.group(3)
            self.is_valid = True
