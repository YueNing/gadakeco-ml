import random

from render import renderentity
from util import texturehandler
from worldgeneration.entityfactory import EntityFactory


class RenderEntityFactory(EntityFactory):
    """
    factory for creating rendered entities
    """

    def __init__(self):
        EntityFactory.__init__(self)
        self.currenttexture = texturehandler.Textures.cobblestone

    def chooseRandomTexture(self):
        self.currenttexture = random.choice(texturehandler.blocks)

    def createBlock(self, x, y, w, h):
        entity = EntityFactory.createBlock(self, x, y, w, h)
        entity.renderer = renderentity.RenderBase(entity, self.currenttexture)
        return entity

    def createCoin(self, x, y):
        entity = EntityFactory.createCoin(self, x, y)
        # TODO: swap to RenderLiving (rotating coin)
        entity.renderer = renderentity.RenderBase(entity, texturehandler.Textures.coin)
        return entity

    def createEnemy(self, x, y):
        entity = EntityFactory.createEnemy(self, x, y)
        entity.renderer = renderentity.RenderLiving(entity, random.choice(texturehandler.enemies))
        return entity

    def cycle(self):
        # reset texture for next cycle
        self.chooseRandomTexture()
