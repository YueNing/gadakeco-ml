from gui.guielement import GuiElement
from lib.constants import screenWidth


class GuiLabel(GuiElement):
    """
    A simple label
    """

    def __init__(self, x, y, fontObj, text="", color=(255, 255, 255)):
        GuiElement.__init__(self, x, y, *fontObj.size(text), fontObj)
        self._text = text
        self._textSurf = self._fontObj.render(text, 1, color)

    def setText(self, text, color=(255, 255, 255)):
        self._text = text
        self._textSurf = self._fontObj.render(text, 1, color)
        self._aabb.width = self._textSurf.get_width()
        self._aabb.height = self._textSurf.get_height()

    def update(self, t):
        pass

    def draw(self, screen):
        screen.blit(self._textSurf, (self.getX(), self.getY()))

    @classmethod
    def createCentered(self, y, fontObj, text="", color=(255, 255, 255)):
        x = int((screenWidth - fontObj.size(text)[0]) / 2.0)
        return GuiLabel(x, y, fontObj, text, color)
