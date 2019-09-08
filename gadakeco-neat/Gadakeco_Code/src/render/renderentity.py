import random

import pygame

from lib.config import Entries
from util import texturehandler
from util.soundhandler import Sound
from util.texturehandler import Textures


class RenderBase:
    """
    renderer for entities
    """

    def __init__(self, entity, texture):
        self._entity = entity
        self._texture = texture
        self._surf = self.createSurface()

    def createSurface(self):
        surf = pygame.Surface((self._entity.getWidth(), self._entity.getHeight()), 0, self._texture.surface)
        return texturehandler.fillSurface(surf, self._texture)

    def render(self, screen, world):
        screen.blit(self._surf, self._entity.getCamRelPos(world.camera))
        if Entries.ShowDebug.getCurrentValue():
            pygame.draw.rect(screen, (0, 255, 0), (
            *self._entity.getCamRelPos(world.camera), self._entity.getWidth(), self._entity.getHeight()), 1)


class RenderLiving(RenderBase):
    """
    renderer for living entities
    """

    def __init__(self, entity, texture):
        RenderBase.__init__(self, entity, texture)

    def createSurface(self):
        adjustedWidth = self._texture.surface.get_width() * self._entity.getHeight() / self._texture.surface.get_height()
        if adjustedWidth % self._entity.getWidth() != 0:
            raise ValueError(str(self._texture) + "has no matching width/height-ratio for this entity")
        self._frameCount = int(adjustedWidth / self._entity.getWidth())
        if self._frameCount < 2:
            raise ValueError(
                str(self._texture) + " has to have at least 2 frames to use for a living entity (standing + moving)")

        surf = pygame.transform.scale(self._texture.surface,
                                      (self._entity.getWidth() * self._frameCount, self._entity.getHeight()))
        return (surf, pygame.transform.flip(surf, True, False))

    def getFrame(self, world, flipped):
        if self._entity._velocityX == 0:
            return (self._frameCount - 1) if flipped else 0
        else:
            frame = 1 + int(world.time * (10 / self._frameCount) % (self._frameCount - 1))
            return self._frameCount - 1 - frame if flipped else frame

    def render(self, screen, world):
        if Entries.ShowDebug.getCurrentValue():
            pygame.draw.rect(screen, (200, 255, 0), (
            self._entity._lastX - world.camera.getX(), self._entity._lastY - world.camera.getY(),
            self._entity.getWidth(), self._entity.getHeight()), 1)

        flipped = self._entity._velocityX < 0
        frame = self.getFrame(world, flipped)
        screen.blit(self._surf[flipped], self._entity.getCamRelPos(world.camera),
                    (frame * self._entity.getWidth(), 0, self._entity.getWidth(), self._entity.getHeight()))


class RenderPlayer(RenderLiving):
    """
    renderer for the player
    """

    def __init__(self, player):
        RenderBase.__init__(self, player, Textures.player)

    def getFrame(self, world, flipped):
        if self._entity._inAir or self._entity._velocityX == 0:
            if self._entity._velocityX == 0:
                return (self._frameCount - 1) if flipped else 0
            else:
                return 0 if flipped else (self._frameCount - 1)
        else:
            frame = 1 + int(world.time * 10 % (self._frameCount - 1))
            return self._frameCount - 1 - frame if flipped else frame

    def render(self, screen, world):
        # TODO: find better location for this
        # jump sound
        if self._entity.jumped:
            Sound.play(random.choice((Sound.jump1, Sound.jump2)))
            self._entity.jumped = False
        # collided with entity and got hurt
        if self._entity.hurt:
            Sound.play(random.choice((Sound.hurt1, Sound.hurt2)))
            self._entity.hurt = False
        # falling into void
        if self._entity.falling:
            Sound.play(Sound.falling)
            self._entity.falling = False

        flipped = self._entity._velocityX < 0
        frame = self.getFrame(world, flipped)
        screen.blit(self._surf[flipped], self._entity.getCamRelPos(world.camera),
                    (frame * self._entity.getWidth(), 0, self._entity.getWidth(), self._entity.getHeight()))

        if Entries.ShowDebug.getCurrentValue():
            pygame.draw.rect(screen, (255, 0, 0), (
            *self._entity.getCamRelPos(world.camera), self._entity.getWidth(), self._entity.getHeight()), 1)
