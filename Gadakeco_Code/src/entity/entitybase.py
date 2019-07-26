import lib.constants as const
from aabb import AABB
from camera import cameraPosX, cameraPosY


class EntityBase:
    """
    all the entities! (blocks, enemies, projectiles)
    """

    def __init__(self, x, y, width, height):
        self._aabb = AABB(x, y, width, height)

    def getMinimapID(self):
        return 1

    def isSolid(self):
        return True

    def getX(self):
        return self._aabb.x

    def getY(self):
        return self._aabb.y

    def getWidth(self):
        return self._aabb.width

    def getHeight(self):
        return self._aabb.height

    def isVisible(self, player):
        horizontal = (
                                 self.getX() + self.getWidth() + const.staticUpdateDist * const.screenWidth * cameraPosX >= player.getX()) and (
                                 self.getX() - const.staticUpdateDist * const.screenWidth * (
                                     1.0 - cameraPosX) <= player.getX() + player.getWidth())
        vertical = (
                               self.getY() + self.getHeight() + const.staticUpdateDist * const.screenHeight * cameraPosY >= player.getY()) and (
                               self.getY() - const.staticUpdateDist * const.screenHeight * (
                                   1.0 - cameraPosY) <= player.getY() + player.getHeight())
        return horizontal and vertical

    def isColliding(self, entity):
        return self._aabb.intersects(entity._aabb)

    def getOverlappingArea(self, entity):
        return self._aabb.getOverlapArea(entity._aabb)

    def getCamRelPos(self, camera):
        return (self.getX() - camera.getX(), self.getY() - camera.getY())

    def __str__(self):
        return str(self._aabb)
