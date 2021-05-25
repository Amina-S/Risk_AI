from enum import Enum


class Color(Enum):
    RED = '\x1b[31m'
    YELLOW = '\x1b[33m'
    GREEN = '\x1b[32m'
    CYAN = '\x1b[36m'
    BLUE = '\x1b[34m'
    PURPLE = '\x1b[35m'
    ENDC = '\033[0m'
    NONE = '\x1b[6;30;42m'

    def __str__(self):
        return self.name

    # def __str__(self):
    #     return self.value + self.name + Color.ENDC.value
