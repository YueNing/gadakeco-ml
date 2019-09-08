from entity.entityliving import EntityLiving
from util.directions import Direction


class EntityEnemy(EntityLiving):
    """
    Basic enemy
    """

    def __init__(self, x, y, width=38, height=38):
        EntityLiving.__init__(self, x, y, width, height)
        self._accelerationX = -70

    def onCollideStatic(self, entityBase, side, world):
        if side == Direction.left:
            self._accelerationX = -35
            self._lastAccelerationX = -35
        elif side == Direction.right:
            self._accelerationX = 35
            self._lastAccelerationX = 35
        elif side == Direction.invalid:
            self.state = -1
