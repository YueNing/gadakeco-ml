import pygame
from pygame.font import Font

from context.basecontext import BaseContext
from gui.guibutton import GuiButton


class GamePauseContext(BaseContext):
    """
    Context for when the game is paused
    """

    def __init__(self, gameContext, setContextFunc):
        BaseContext.__init__(self, setContextFunc)
        self._gameContext = gameContext

        fontObj = Font(None, 40)
        self.addElements({
            "bResume": GuiButton(240, 200, fontObj, "Resume").connect(self.buttonResume),
            "bOptions": GuiButton(240, 300, fontObj, "Options").connect(self.buttonOptions),
            "bHelp": GuiButton(240, 400, fontObj, "Help").connect(self.buttonHelp),
            "bMainMenu": GuiButton(240, 500, fontObj, "Back to main menu").connect(self.buttonMainMenu)
        })

    def draw(self, screen):
        self._gameContext.draw(screen)
        BaseContext.draw(self, screen)

    def handleEvent(self, event):
        if BaseContext.handleEvent(self, event):
            return True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._setContextFunc(self._gameContext)
            return True
        return False

    """
    button press functions
    """

    def buttonResume(self):
        self._setContextFunc(self._gameContext)

    def buttonOptions(self):
        from context.optioncontext import OptionContext
        self._setContextFunc(OptionContext(self, self._setContextFunc))

    def buttonHelp(self):
        from context.helpcontext import HelpContext
        self._setContextFunc(HelpContext(self, self._setContextFunc))

    def buttonMainMenu(self):
        from context.mainmenucontext import MainMenuContext
        self._setContextFunc(MainMenuContext(self._setContextFunc))
