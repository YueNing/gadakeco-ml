import pygame
from pygame.font import SysFont

import render.renderentity as renderent
import util.texturehandler as texhandler
from lib.constants import screenWidth, screenHeight
from worldgeneration.renderentityfactory import RenderEntityFactory


class RenderWorld:
    """
    renderer for worlds
    """

    def __init__(self, world):
        self._world = world
        # update the entityfactory to a rendered version
        self._world.worldgen.ef = RenderEntityFactory()
        # attach the renderer for the player
        self._world.player.renderer = renderent.RenderPlayer(self._world.player)

        # the background texture
        self._background = pygame.transform.scale(texhandler.Textures.gameBG.surface, (2 * screenWidth, screenHeight))
        self._overlays = texhandler.adjustedSurface(texhandler.Textures.overlays, height=32)
        self._fontObj = SysFont("Monospace", 20, bold=True)

    def render(self, screen):
        # draw the backgound
        bgWidth = self._background.get_width()
        x = int((self._world.camera.getX() * 0.1) % bgWidth)

        if x + screenWidth <= bgWidth:
            screen.blit(self._background, (0, 0), (x, 0, x + screenWidth, screenHeight))
        # end of texture reached
        else:
            drawWidth = x + screenWidth - bgWidth
            screen.blit(self._background, (0, 0), (x, 0, x + drawWidth, screenHeight))
            screen.blit(self._background, (screenWidth - drawWidth, 0), (0, 0, drawWidth, screenHeight))

        # draw the static entities (e.g. blocks)
        for ent in self._world.visibleStaticEntities:
            ent.renderer.render(screen, self._world)
        # draw the dynamic entities (enemies, projectiles, ...)
        for ent in self._world.visibleDynamicEntities:
            ent.renderer.render(screen, self._world)
        # draw the player
        self._world.player.renderer.render(screen, self._world)

        # draw the overlay
        self.renderOverlay(screen)

    def renderOverlay(self, screen):
        # draw hearts
        for i in range(3):
            x = 30 + i * 34
            # draw full heart
            if self._world.player.state >= i:
                screen.blit(self._overlays, (x, 15), (0, 0, 32, 32))
            # draw empty heart
            else:
                screen.blit(self._overlays, (x, 15), (32, 0, 32, 32))
        # draw armor if player is invulnerable
        if self._world.player.invulTimer > 0:
            screen.blit(self._overlays, (145, 15), (64, 0, 32, 32))

        x = screenWidth - 170
        # draw seed
        renderedSeed = self._fontObj.render(str(int(self._world.seed)), 1, (0, 0, 0))
        screen.blit(self._overlays, (x, 15), (192, 0, 32, 32))
        screen.blit(renderedSeed, (x + 42, 22))

        # draw time
        x -= 170
        renderedTime = self._fontObj.render("{0:.2f}".format(self._world.time), 1, (0, 0, 0))
        screen.blit(self._overlays, (x, 15), (96, 0, 32, 32))
        screen.blit(renderedTime, (x + 42, 22))

        # draw points
        x -= 170
        renderedPoints = self._fontObj.render(str(int(self._world.points)), 1, (0, 0, 0))
        screen.blit(self._overlays, (x, 15), (128, 0, 32, 32))
        screen.blit(renderedPoints, (x + 42, 22))


class RenderNeuronalWorld(RenderWorld):
    """
    renderer for neuronal worlds
    """

    def renderOverlay(self, screen):
        RenderWorld.renderOverlay(self, screen)

        # draw fitness
        renderedFitness = self._fontObj.render("{0:.2f}".format(self._world.nn.fitness), 1, (0, 0, 0))
        screen.blit(self._overlays, (300, 15), (160, 0, 32, 32))
        screen.blit(renderedFitness, (342, 22))
