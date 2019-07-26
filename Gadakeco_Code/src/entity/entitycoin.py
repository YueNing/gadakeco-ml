from entity.entitybase import EntityBase
from entity.entityliving import EntityLiving


class EntityCoin(EntityLiving):
    """
    simple entity for coins
    """

    def __init__(self, x, y):
        EntityLiving.__init__(self, x, y, 40, 40)

    def getMinimapID(self):
        return 0

    def isSolid(self):
        return False

    def isVisible(self, player):
        return EntityBase.isVisible(self, player)

    def move(self, t):
        pass

    def updateAndIsAlive(self, world, t):
        return self.isAlive()
