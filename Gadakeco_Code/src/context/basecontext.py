import sys

import pygame

from lib.constants import FPS, MAX_DELTA


class BaseContext():
    """
    the base class for all ContextManagers
    """

    def __init__(self, setContextFunc):
        self._setContextFunc = setContextFunc
        self._elements = {}
        self._wasMouseDown = False

    def addElement(self, name, element):
        self._elements[name] = element

    def addElements(self, dictionary):
        self._elements.update(dictionary)

    def calculateDelta(self, clock):
        sElapsed = clock.tick(FPS) / 1000.0
        # prevent too high delta (e.g. caused by dragging the window)
        return min(sElapsed, MAX_DELTA)

    def update(self, sElapsed):
        for element in self._elements.values():
            element.update(sElapsed)
        for event in pygame.event.get():
            self.handleEvent(event)

    def draw(self, screen):
        for element in self._elements.values():
            element.draw(screen)

    def closeApp(self):
        pygame.quit()
        sys.exit()

    def handleEvent(self, event):
        if event.type == pygame.QUIT:
            self.closeApp()
            return True

        for element in self._elements.values():
            if element.canHandleEvent(event) and element.handleEvent(event):
                return True

        return False
