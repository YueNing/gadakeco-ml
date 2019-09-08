from entity.entitybase import EntityBase
from entity.entitycoin import EntityCoin
from entity.entityenemy import EntityEnemy


class EntityFactory:
    """
    factory for creating entities
    """

    def __init__(self):
        self._createdEntities = []

    def createBlock(self, x, y, w, h):
        entity = EntityBase(x, y, w, h)
        return entity

    def createCoin(self, x, y):
        entity = EntityCoin(x, y)
        return entity

    def createEnemy(self, x, y):
        entity = EntityEnemy(x, y)
        return entity

    def cycle(self):
        pass
