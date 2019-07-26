import random

from pygame import Surface
from pygame.font import Font

from context.basecontext import BaseContext
from gui.guibutton import GuiButton
from gui.guilabel import GuiLabel
from lib import constants
from util import texturehandler


class HelpContext(BaseContext):
    """
    Context for the help screen
    """

    def __init__(self, parent, setContextFunc):
        BaseContext.__init__(self, setContextFunc)
        self._parent = parent
        self._background = texturehandler.fillSurface(Surface(constants.screenSize),
                                                      random.choice(texturehandler.blocks), (64, 64))
        self._overlays = texturehandler.adjustedSurface(texturehandler.Textures.overlays, height=48)

        self.addElements({
            "lCaption": GuiLabel.createCentered(10, Font(None, 60), "Help"),
            "bBack": GuiButton(240, 600, Font(None, 40), "Back").connect(self.buttonBack)
        })
        self.addIconHelp()

    def addIconHelp(self):
        descFont = Font(None, 30)
        descriptions = ("the remaining lifes of the player",
                        "the lifes the player has lost",
                        "indicates player-invulnerability",
                        "the time",
                        "the points earned",
                        "fitness (of a neuronal network)",
                        "the seed of the world generator",
                        "generation (of a neuronal network)"
                        )

        def getPos(i):
            x = 500 * ((55 * i) // 495)
            y = (55 * i) % 495
            return (x, y)

        self._positions = [0] * len(descriptions)
        i = 0
        for desc in descriptions:
            self._positions[i] = getPos(i)
            self.addElement("lIcon{}".format(i),
                            GuiLabel(110 + self._positions[i][0], 85 + self._positions[i][1], descFont, desc))
            i += 1

    def draw(self, screen):
        screen.blit(self._background, (0, 0))
        BaseContext.draw(self, screen)

        for i, (x, y) in enumerate(self._positions):
            screen.blit(self._overlays, (50 + x, 70 + y), (i * 48, 0, 48, 48))

    """
    button press functions
    """

    def buttonBack(self):
        self._setContextFunc(self._parent)
