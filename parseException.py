from .constants import Color

class ParseException(Exception):
    def __init__(self, reason = ''):
        self.reason = reason

    def __str__(self):
        return Color.BOLD + Color.RED + self.reason + Color.END