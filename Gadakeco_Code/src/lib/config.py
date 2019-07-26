import json
from enum import Enum
from json.decoder import JSONDecodeError

import pygame

from lib import constants

_filePath = constants.res_loc() + "config.json"
_values = {}


class EntryType(Enum):
    # lambda for converting key values to strings
    Key = (0, lambda value: pygame.key.name(value).capitalize())
    Toggle = (1, str)
    Scroll = (2, str)

    def __init__(self, index, func):
        self._value_ = index
        self.func = func


class Entries(Enum):
    """
    Enumeration of all possible settings with it's default value
    """
    KeyLeft = ("Move left", pygame.K_a, EntryType.Key)
    KeyRight = ("Move right", pygame.K_d, EntryType.Key)
    KeySpace = ("Jump", pygame.K_SPACE, EntryType.Key)
    ShowDebug = ("Debug mode", False, EntryType.Toggle)
    MusicVolume = ("Music volume", 1.0, EntryType.Scroll)
    SoundVolume = ("Sound volume", 1.0, EntryType.Scroll)

    def __init__(self, desc, default, entryType):
        self.desc = desc
        self.default = default
        self.entryType = entryType

    def getCurrentValue(self):
        return _values[self.name]

    def setCurrentValue(self, value):
        global _values
        _values[self.name] = value

    def __str__(self):
        return self.entryType.func(self.getCurrentValue())


def init():
    loadConfig()


def resetConfig():
    global _values
    _values.clear()
    for entry in Entries:
        _values[entry.name] = entry.default


def loadConfig():
    global _values
    try:
        with open(_filePath, "r") as file:
            _values = json.load(file)
        resolveComplete()
    except (FileNotFoundError, JSONDecodeError):
        resetConfig()
        saveConfig()


def saveConfig():
    with open(_filePath, "w") as file:
        json.dump(_values, file, indent=4)


def resolveComplete():
    global _values

    update = False
    for entry in Entries:
        if entry.name not in _values:
            update = True
            _values[entry.name] = entry.default
    if update:
        saveConfig()
