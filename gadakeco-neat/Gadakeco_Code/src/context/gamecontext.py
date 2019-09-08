import pygame

from context.basecontext import BaseContext
from context.gameovercontext import GameOverContext
from render.renderworld import RenderWorld
from world import World


class GameContext(BaseContext):
    """
    ContextManager for the game itself
    """

    def __init__(self, seed, setContextFunc):
        BaseContext.__init__(self, setContextFunc)
        self.setWorld(World(seed))

        # disable key repeats
        pygame.key.set_repeat()

    def getWorld(self):
        return self._world

    def setWorld(self, world):
        self._world = world
        self._world.renderer = RenderWorld(self._world)
        self._world.generatePlatform()

    def update(self, t):
        BaseContext.update(self, t)
        if not self._world.update(t):
            self._setContextFunc(GameOverContext(self, self._setContextFunc))

    def draw(self, screen):
        self._world.renderer.render(screen)

    def handleEvent(self, event):
        if BaseContext.handleEvent(self, event):
            return True

        from context.gamepausecontext import GamePauseContext
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._setContextFunc(GamePauseContext(self, self._setContextFunc))

        return False
