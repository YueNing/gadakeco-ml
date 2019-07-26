import pygame

from gui.guielement import GuiElement
from util.soundhandler import Sound


class GuiButton(GuiElement):
    def __init__(self, x, y, fontObj, text, width=600, height=50, textColor=(0, 0, 0), startColor=(0, 100, 255),
                 endColor=(0, 200, 255)):
        GuiElement.__init__(self, x, y, width, height, fontObj)
        self._hovered = False
        self._text = text
        self._textColor = textColor
        self._textSurf = self._fontObj.render(text, 1, textColor)
        self._func = None
        self._wasMouseDown = False
        self.enabled = True
        self.setEventTypes(pygame.MOUSEBUTTONDOWN)
        # create the gradient
        self.createSurface(startColor, endColor)

    def connect(self, func, *params):
        self._func = func
        self._params = params
        return self

    def setText(self, text):
        self._text = text
        self._textSurf = self._fontObj.render(text, 1, self._textColor)

    def getText(self):
        return self._text

    def createSurface(self, startColor, endColor):
        self._surface = pygame.surface.Surface((self.getWidth(), self.getHeight()))
        for y in range(self.getHeight()):
            t = y / (self.getHeight() - 1)
            color = (int((1 - t) * startColor[0] + t * endColor[0]), int((1 - t) * startColor[1] + t * endColor[1]),
                     int((1 - t) * startColor[2] + t * endColor[2]))
            for x in range(self.getWidth()):
                self._surface.set_at((x, y), color)

    def update(self, t):
        if not self.enabled:
            return

        mouseX, mouseY = pygame.mouse.get_pos()
        if self._aabb.contains(mouseX, mouseY):
            self._hovered = True
        else:
            self._hovered = False

    def canHandleEvent(self, event):
        return GuiElement.canHandleEvent(self, event) and event.button == 1

    def handleEvent(self, event):
        if self.enabled and self._hovered and self._func != None:
            Sound.play(Sound.buttonClick)
            self._func(*self._params)
            return True
        else:
            return False

    def draw(self, screen):
        screen.blit(self._surface, (self.getX(), self.getY()))
        if self.enabled:
            if self._hovered:
                screen.fill((50, 50, 50), self.getRect(), pygame.BLEND_ADD)
        else:
            screen.fill((100, 100, 100), self.getRect())

        textX = self.getX() + (self.getWidth() - self._textSurf.get_width()) / 2.0
        textY = self.getY() + (self.getHeight() - self._textSurf.get_height()) / 2.0 + 1
        screen.blit(self._textSurf, (textX, textY))
