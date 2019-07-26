import random

import pygame
from pygame.font import Font, SysFont

from context.basecontext import BaseContext
from gui.guibutton import GuiButton
from gui.guilabel import GuiLabel
from gui.guitextfield import GuiNumberTextfield
from lib.constants import screenSize
from util import texturehandler
from util.soundhandler import Music


class StartGameContext(BaseContext):
    """
    Context for the starting game screen
    """

    def __init__(self, mainMenuContext, setContextFunc):
        BaseContext.__init__(self, setContextFunc)
        self._mainMenuContext = mainMenuContext
        fontObj = Font(None, 40)
        self._background = texturehandler.fillSurface(pygame.Surface(screenSize), random.choice(texturehandler.blocks),
                                                      (64, 64))

        self.addElements({
            "lCaption": GuiLabel.createCentered(10, Font(None, 60), "Starting new Game"),
            "lSeed": GuiLabel.createCentered(280, fontObj, "Seed for the World Generator"),
            "tfSeed": GuiNumberTextfield(430, 325, SysFont("Monospace", 38, bold=True), width=220),
            "lHint": GuiLabel.createCentered(400, fontObj, "leave blank for a random seed", color=(200, 200, 200)),
            "bBack": GuiButton(240, 500, fontObj, "Back", width=285).connect(self.buttonBack),
            "bStartGame": GuiButton(555, 500, fontObj, "Start Game", width=285).connect(self.buttonStartGame)
        })

        self._elements["tfSeed"].setFocused(True)

        # enable key repeats
        pygame.key.set_repeat(500, 50)

    def getSeed(self):
        seed = self._elements["tfSeed"].getText()
        if not seed:
            seed = random.randint(0, 1000)
        else:
            seed = int(seed)
        return seed

    def draw(self, screen):
        screen.blit(self._background, (0, 0))
        BaseContext.draw(self, screen)

    """
    button press functions
    """

    def buttonStartGame(self):
        from context.gamecontext import GameContext
        seed = self.getSeed()
        Music.stop()
        self._setContextFunc(GameContext(seed, self._setContextFunc))

    def buttonBack(self):
        self._setContextFunc(self._mainMenuContext)
