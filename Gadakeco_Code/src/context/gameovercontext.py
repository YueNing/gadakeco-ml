from pygame.font import Font

from context.basecontext import BaseContext
from gui.guibutton import GuiButton
from gui.guilabel import GuiLabel
from world import World


class GameOverContext(BaseContext):
    """
    Context for when the player died
    """

    def __init__(self, gameContext, setContextFunc):
        BaseContext.__init__(self, setContextFunc)
        self._gameContext = gameContext
        self._fontObj = Font(None, 40)

        self.addElements({
            "lGameOver": GuiLabel.createCentered(120, Font(None, 130), "Game Over!", (255, 0, 0)),
            "lSeed": GuiLabel.createCentered(220, self._fontObj, "Your score is " + str(
                int(gameContext._world.points)) + ", Your seed: " + str(gameContext._world.seed), (0, 0, 0)),
            "bRetry": GuiButton(240, 520, self._fontObj, "Retry").connect(self.buttonRetry),
            "bMainMenu": GuiButton(240, 600, self._fontObj, "Back to main menu").connect(self.buttonMainMenu)
        })

    def draw(self, screen):
        self._gameContext.draw(screen)
        BaseContext.draw(self, screen)

    def buttonRetry(self):
        self._gameContext.setWorld(World(self._gameContext.getWorld().seed))
        self._setContextFunc(self._gameContext)

    def buttonMainMenu(self):
        from context.mainmenucontext import MainMenuContext
        self._setContextFunc(MainMenuContext(self._setContextFunc))
