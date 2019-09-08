import pygame
from pygame.font import Font

import lib.constants as const
from context.basecontext import BaseContext
from gui.guibutton import GuiButton
from lib.config import Entries
from util import texturehandler
from util.soundhandler import Music


class MainMenuContext(BaseContext):
    """
    Context for the main menu
    """

    def __init__(self, setContextFunc):
        BaseContext.__init__(self, setContextFunc)
        self._background = texturehandler.fillSurface(pygame.Surface(const.screenSize),
                                                      texturehandler.Textures.cobblestone, (64, 64))
        # adjust logo to dimensions (adjustedWidth, 120)
        self._logo = texturehandler.adjustedSurface(texturehandler.Textures.logo, height=130)

        fontObj = Font(None, 40)
        self.addElements({
            "bStartGame": GuiButton(240, 200, fontObj, "Start Game").connect(self.buttonStartGame),
            "bNeuronalNetworking": GuiButton(240, 280, fontObj, "Neuronal Networking").connect(self.buttonNetworks),
            "bOptions": GuiButton(240, 440, fontObj, "Options").connect(self.buttonOptions),
            "bHelp": GuiButton(240, 520, fontObj, "Help").connect(self.buttonHelp),
            "bQuit": GuiButton(240, 600, fontObj, "Quit").connect(self.closeApp)
        })

        Music.setVolume(Entries.MusicVolume.getCurrentValue())
        Music.play(Music.bgMusic, 0)

    def draw(self, screen):
        screen.blit(self._background, (0, 0))
        screen.blit(self._logo, ((const.screenWidth - self._logo.get_width()) // 2, 35))
        BaseContext.draw(self, screen)

    """
    button press functions
    """

    def buttonStartGame(self):
        from context.startgamecontext import StartGameContext
        self._setContextFunc(StartGameContext(self, self._setContextFunc))

    def buttonNetworks(self):
        from context.networkcontext import NetworkContext
        self._setContextFunc(NetworkContext(self, self._setContextFunc))

    def buttonOptions(self):
        from context.optioncontext import OptionContext
        self._setContextFunc(OptionContext(self, self._setContextFunc))

    def buttonHelp(self):
        from context.helpcontext import HelpContext
        self._setContextFunc(HelpContext(self, self._setContextFunc))
