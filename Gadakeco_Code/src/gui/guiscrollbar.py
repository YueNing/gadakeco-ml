import pygame

from gui.guielement import GuiElement

HORIZONTAL = 0
VERTICAL = 1


class GuiScrollbar(GuiElement):
    """
    scrollbar / slider
    """

    def __init__(self, x, y, width, height, fontObj, value=0.0, orientation=HORIZONTAL, barLength=30):
        GuiElement.__init__(self, x, y, width, height, fontObj)
        self._value = value
        self._orientation = orientation
        self._barLength = barLength
        self.setEventTypes(pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION)
        self._grabbed = False
        self._func = None

    def getValue(self):
        return self._value

    def setValue(self, value):
        self._value = min(max(value, 0), 1)

    def connect(self, func, *params):
        self._func = func
        self._params = params
        return self

    def update(self, t):
        pass

    def canHandleEvent(self, event):
        return GuiElement.canHandleEvent(self, event)

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._aabb.contains(*pygame.mouse.get_pos()):
                self._grabbed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._grabbed:
                self._grabbed = False
                if self._func != None:
                    self._func(*self._params)
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self._grabbed:
                if self._orientation == HORIZONTAL:
                    self.setValue(
                        (event.pos[0] - self._barLength / 2.0 - self.getX()) / (self.getWidth() - self._barLength))
                else:
                    self.setValue(
                        (event.pos[1] - self._barLength / 2.0 - self.getY()) / (self.getHeight() - self._barLength))
                return True
        return False

    def draw(self, screen):
        screen.fill((50, 50, 50), self.getRect())

        if self._orientation == HORIZONTAL:
            y = self.getY() + self.getHeight() / 2.0 - 1
            screen.fill((255, 255, 255), (self.getX(), y, self.getWidth(), 2))

            barX = self.getX() + self._value * (self.getWidth() - self._barLength)
            screen.fill((100, 200, 255), (barX, self.getY(), self._barLength, self.getHeight()))
        else:
            x = self.getX() + self.getWidth() / 2.0 - 1
            screen.fill((255, 255, 255), (x, self.getY(), 2, self.getHeight()))

            barY = self.getY() + self._value * (self.getHeight() - self._barLength)
            screen.fill((100, 200, 255), (self.getX(), barY, self.getWidth(), self._barLength))
