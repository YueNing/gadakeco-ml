from builtins import classmethod
from enum import Enum

import pygame.mixer as mixer

from lib import constants
from lib.config import Entries

mixer.init()


class Music(Enum):
    bgMusic = "bensound-relaxing.ogg"

    def __init__(self, fileName):
        self._value_ = constants.res_loc("music") + fileName

    @classmethod
    def play(cls, music, repeats=1):
        mixer.music.stop()
        mixer.music.load(music.value)
        mixer.music.play(repeats - 1)

    @classmethod
    def stop(cls):
        # mixer.music.stop()
        mixer.music.fadeout(1000)

    @classmethod
    def setVolume(cls, value):
        mixer.music.set_volume(value)


class Sound(Enum):
    buttonClick = "buttonClick.wav"
    jump1 = "jump1.ogg"
    jump2 = "jump2.ogg"
    hurt1 = "hurt1.wav"
    hurt2 = "hurt2.wav"
    falling = "boneCrushing.wav"

    def __init__(self, fileName):
        self._value_ = mixer.Sound(constants.res_loc("sounds") + fileName)

    @classmethod
    def play(cls, sound):
        sound.value.set_volume(Entries.SoundVolume.getCurrentValue())
        sound.value.play()
