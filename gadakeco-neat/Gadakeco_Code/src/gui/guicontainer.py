import pygame

from gui import guiscrollbar
from gui.guielement import GuiElement


class GuiContainer(GuiElement):
    """
    a container for gui elements
    """

    def __init__(self, x, y, width, height, fontObj):
        GuiElement.__init__(self, x, y, width, height, fontObj)
        self._scrollBar = guiscrollbar.GuiScrollbar(x + width - 30, y, 30, height, fontObj,
                                                    orientation=guiscrollbar.VERTICAL)
        self._elements = {}
        self._maxScrollDistance = 1

    def addElement(self, name, guiElement):
        self._elements[name] = (guiElement, guiElement.getX(), guiElement.getY())
        # update maxY
        self._maxScrollDistance = max(self._maxScrollDistance, guiElement.getY() + guiElement.getHeight())
        # move element into position
        guiElement.setX(self.getX() + guiElement.getX())
        guiElement.setY(self.getY() + guiElement.getY())

    def clearElements(self):
        self._elements.clear()

    def __getitem__(self, key):
        return self._elements[key][0]

    def update(self, t):
        self._scrollBar.update(t)
        for element in self._elements.values():
            if self._aabb.intersects(element[0]._aabb):
                element[0].update(t)

    def canHandleEvent(self, event):
        return True

    def handleEvent(self, event):
        # scrolling with mouse wheel
        if event.type == pygame.MOUSEBUTTONDOWN and self._aabb.contains(*event.pos):
            if event.button == 4 or event.button == 5:
                scrollAmount = self.getHeight() / self._maxScrollDistance
                scrollAmount = scrollAmount * scrollAmount
                if event.button == 4:
                    scrollAmount *= -1

                self._scrollBar.setValue(self._scrollBar.getValue() + scrollAmount)
                self.updatePositions()
                return True

        if self._scrollBar.canHandleEvent(event) and self._scrollBar.handleEvent(event):
            self.updatePositions()
            return True

        for element in self._elements.values():
            if element[0].canHandleEvent(event) and element[0].handleEvent(event):
                return True
        return False

    def updatePositions(self):
        scrollHeight = max(self._maxScrollDistance + 10 - self.getHeight(), 0)
        for element, relX, relY in self._elements.values():
            element.setY(self.getY() + relY - self._scrollBar.getValue() * scrollHeight)

    def draw(self, screen):
        screen.set_clip(self.getRect())
        screen.fill((70, 70, 70))

        self._scrollBar.draw(screen)
        for element in self._elements.values():
            if self._aabb.intersects(element[0]._aabb):
                element[0].draw(screen)

        screen.set_clip()
