import os
import random

import pygame
from pygame.font import Font, SysFont

from context.basecontext import BaseContext
from gui.guibutton import GuiButton
from gui.guicontainer import GuiContainer
from gui.guilabel import GuiLabel
from gui.guitextfield import GuiNumberTextfield
from lib import constants
from lib.constants import screenSize
from util import texturehandler
from util.soundhandler import Music


class NetworkContext(BaseContext):
    """
    Context for neuronal networks
    """

    def __init__(self, mainMenuContext, setContextFunc):
        BaseContext.__init__(self, setContextFunc)
        self._mainMenuContext = mainMenuContext
        self._background = texturehandler.fillSurface(pygame.Surface(screenSize), random.choice(texturehandler.blocks),
                                                      (64, 64))
        self._files = []
        self.initGuiElements()

        # enable key repeats
        pygame.key.set_repeat(500, 50)

    def initGuiElements(self):
        self._elements.clear()

        fontObj = Font(None, 40)
        self.addElements({
            "lCaption": GuiLabel.createCentered(10, Font(None, 60), "Neuronal Networking"),
            "lNetworks": GuiLabel(100, 70, fontObj, "Your Networks:"),
            "cNetworks": GuiContainer(100, 110, 350, 450, fontObj),
            "lSeed": GuiLabel(525, 220, fontObj, "Seed for the World Generator"),
            "tfSeed": GuiNumberTextfield(610, 260, SysFont("Monospace", 38, bold=True), width=220),
            "lHint": GuiLabel(520, 330, fontObj, "leave blank for a random seed", color=(200, 200, 200)),
            "bCreateNetwork": GuiButton(570, 380, fontObj, "Create New Network", width=300).connect(
                self.buttonCreateNetwork),
            "bBack": GuiButton(240, 600, fontObj, "Back").connect(self.buttonBack)
        })
        self._elements['tfSeed'].setFocused(True)
        self.updateNetworks()

    def updateNetworks(self):
        dirEntries = os.scandir(constants.res_loc("networks"))
        dirEntries = sorted(dirEntries, key=lambda entry: entry.stat().st_mtime, reverse=True)
        self._elements['cNetworks'].clearElements()

        font = Font(None, 32)
        y = 10
        for dirEntry in dirEntries:
            button = GuiButton(10, y, font, dirEntry.name[:dirEntry.name.rfind('.')], width=300, height=30,
                               startColor=(150, 150, 150), endColor=(200, 200, 200)).connect(self.buttonEditNetwork,
                                                                                             dirEntry.name)
            self._elements['cNetworks'].addElement("b" + dirEntry.name, button)
            y += 40

    def getSeed(self):
        seed = self._elements['tfSeed'].getText()
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

    def buttonEditNetwork(self, fileName):
        from context.networkeditcontext import NetworkEditContext
        self._setContextFunc(NetworkEditContext(self, self._setContextFunc, fileName))

    def buttonCreateNetwork(self):
        from context.networktrainingcontext import NNTraningContext
        Music.stop()
        self._setContextFunc(NNTraningContext(self.getSeed(), self._setContextFunc))

    def buttonBack(self):
        self._setContextFunc(self._mainMenuContext)
