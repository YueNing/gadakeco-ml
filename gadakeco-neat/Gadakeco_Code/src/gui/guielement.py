from abc import ABCMeta, abstractmethod

import pygame

from aabb import AABB


class GuiElement(metaclass=ABCMeta):
    def __init__(self, x, y, width, height, fontObj):
        self._aabb = AABB(x, y, width, height)
        self._fontObj = fontObj
        self._eventTypes = ()

    def getX(self):
        return self._aabb.x

    def getY(self):
        return self._aabb.y

    def setX(self, x):
        self._aabb.x = x

    def setY(self, y):
        self._aabb.y = y

    def getWidth(self):
        return self._aabb.width

    def getHeight(self):
        return self._aabb.height

    def getRect(self):
        return pygame.Rect(self._aabb.x, self._aabb.y, self._aabb.width, self._aabb.height)

    def contains(self, x, y):
        return self._aabb.contains(x, y)

    def setEventTypes(self, *types):
        self._eventTypes = types

    def canHandleEvent(self, event):
        return event.type in self._eventTypes

    def handleEvent(self, event):
        return False

    @abstractmethod
    def update(self, t):
        pass

    @abstractmethod
    def draw(self, screen):
        pass
