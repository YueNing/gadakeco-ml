from enum import Enum

import pygame

from lib import constants


def _loadImage(name):
    return pygame.image.load(constants.res_loc("textures") + name)


class Textures(Enum):
    # miscellaneous
    logo = ("logo.png", True)
    # blocks
    cobblestone = ("cobblestone.png", False)
    stone = ("stone.png", False)
    wood_log = ("wood_log.png", False)
    wood_planks = ("wood_planks.png", False)
    # coin
    coin = ("coin.png", True)
    # enemies
    slime = ("enemy_slime.png", True)
    # other game related stuff
    gameBG = ("game_bg.png", False)
    player = ("game_player.png", True)
    overlays = ("overlays.png", True)

    def __init__(self, file, alpha):
        if alpha:
            self.surface = _loadImage(file).convert_alpha()
        else:
            self.surface = _loadImage(file).convert()


"""
All block textures
"""
blocks = (Textures.cobblestone, Textures.stone, Textures.wood_planks, Textures.wood_log)
# TODO make more enemy textures
enemies = (Textures.slime,)


def adjustedSurface(texture, width=-1, height=-1):
    if width == -1:
        adjustedWidth = texture.surface.get_width() * height // texture.surface.get_height()
        return pygame.transform.scale(texture.surface, (adjustedWidth, height))
    elif height == -1:
        adjustedHeight = texture.surface.get_height() * width // texture.surface.get_width()
        return pygame.transform.scale(texture.surface, (width, adjustedHeight))
    else:
        return pygame.transform.scale(texture.surface, (width, height))


def fillSurface(surface, texture, desiredDimensions=(40, 40)):
    # scale texture down to the desiredDimensions
    texture = pygame.transform.scale(texture.surface, desiredDimensions)
    x = 0
    y = 0
    while y < surface.get_height():
        while x < surface.get_width():
            surface.blit(texture, (x, y))
            x += texture.get_width()
        x = 0
        y += texture.get_height()

    return surface


def fitAndFillSurface(surface, texture):
    sWidth = surface.get_width()
    sHeight = surface.get_height()
    var = 0

    if sWidth <= sHeight:
        texture = pygame.transform.scale(texture.value, (sWidth, sWidth))
        while var < sHeight:
            surface.blit(texture, (0, var))
            var += texture.get_height()
    else:
        texture = pygame.transform.scale(texture.value, (sHeight, sHeight))
        while var < sWidth:
            surface.blit(texture, (var, 0))
            var += texture.get_width()

    return surface
