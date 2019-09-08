import math
import os
from builtins import classmethod, SyntaxError
from random import Random

from PIL import Image

from lib import constants
from lib.constants import screenWidth
from worldgeneration.entityfactory import EntityFactory


class WorldSlice():
    """
    represents a tile-version of a world slice loaded from an image
    """

    def __init__(self, blocks, coins, livings, heightDelta):
        self._blocks = blocks
        self._coins = coins
        self._livings = livings
        self._heightDelta = heightDelta

    def generate(self, worldGen):
        currentX = screenWidth + 2 * screenWidth * worldGen.step

        staticEntities = []
        for block in self._blocks:
            bEnt = worldGen.ef.createBlock(currentX + 40 * block[0], worldGen.currentHeight + 40 * block[1],
                                           40 * block[2], 40 * block[3])
            staticEntities.append(bEnt)

        dynamicEntities = []
        for coin in self._coins:
            cEnt = worldGen.ef.createCoin(currentX + 40 * coin[0], worldGen.currentHeight + 40 * coin[1])
            dynamicEntities.append(cEnt)

        for living in self._livings:
            lEnt = worldGen.ef.createEnemy(currentX + 40 * living[0], worldGen.currentHeight + 40 * living[1])
            dynamicEntities.append(lEnt)

        worldGen.currentHeight += 40 * self._heightDelta

        return (staticEntities, dynamicEntities)

    @classmethod
    def parseAll(cls):
        files = os.listdir(constants.res_loc("levels"))
        return tuple(WorldSlice._parseFromImage(file) for file in sorted(files))

    # parses blocks and enemies from an image file
    @classmethod
    def _parseFromImage(cls, fileName):
        image = Image.open(constants.res_loc("levels") + fileName)
        if image.width != 54:
            raise ValueError(
                "WorldSlice " + fileName + " is " + str(image.width) + " pixels wide, but has to be 54 pixels")

        data = list(image.getdata())
        startY = -1
        endY = -1

        # stores the image data row-wise
        for x in range(image.width):
            for y in range(image.height):
                index = x + y * image.width
                color = data[index]

                # air
                if color[3] == 0 or (color[0] == 255 and color[1] == 255 and color[2] == 255):
                    data[index] = 0
                # coin
                elif color[0] == 255 and color[1] == 255 and color[2] == 0:
                    data[index] = 2
                # living
                elif color[0] == 255 and color[1] == 0 and color[2] == 0:
                    data[index] = 3
                # block
                else:
                    data[index] = 1

                    # set start and end-height of this slice
                    if startY == -1:
                        startY = y
                    endY = y

        if startY == -1:
            raise SyntaxError

        blocks = []
        coins = []
        livings = []

        # filters out coins, livings and "long" horizontal blocks (more than 1 tile wide)
        for y in range(image.height):
            tileSize = 0
            for x in range(image.width):
                index = x + y * image.width
                # coin
                if data[index] == 2:
                    coins.append((x, y - startY))
                    data[index] = 0
                # living
                if data[index] == 3:
                    livings.append((x, y - startY))
                    data[index] = 0
                # air
                elif data[index] == 0:
                    if tileSize > 1:
                        blocks.append((x - 1 - (tileSize - 1), y - startY, tileSize, 1))
                        for i in range(tileSize):
                            data[index - (1 + i)] = 0
                    tileSize = 0
                # block
                else:
                    tileSize += 1
            # end of row -> create block if there were more than 1 adjacent blocks at the end of this row
            if tileSize > 1:
                blocks.append((image.width - 1 - (tileSize - 1), y - startY, tileSize, 1))
                for i in range(tileSize):
                    data[image.width - (1 + i) + y * image.width] = 0

        # parses the remaining blocks
        for x in range(image.width):
            tileSize = 0
            for y in range(image.height):
                index = x + y * image.width
                # "air"
                if data[index] == 0:
                    if tileSize > 0:
                        blocks.append((x, y - startY - tileSize, 1, tileSize))
                    tileSize = 0
                # can only be 1 (= block)
                else:
                    tileSize += 1
            # end of column -> create block if there was at least 1 block at the end of this column
            if tileSize > 0:
                blocks.append((x, image.height - startY - tileSize, 1, tileSize))

        return WorldSlice(blocks, coins, livings, endY - startY)


worldSlices = WorldSlice.parseAll()


class WorldGen:
    def __init__(self, world):
        self._world = world
        self._random = Random(world.seed)
        self.step = 0
        self.currentHeight = 640
        self.ef = EntityFactory()

    '''
    generate 2x screenWidth pixels of entities
    '''

    def generateWorldSlice(self):
        currentX = screenWidth + 2 * screenWidth * self.step
        # TODO: ShowDebug not initialized
        #         if Entries.ShowDebug.getCurrentValue():
        #             print("Generating world from " + str(currentX) + " to " + str(currentX + 2 * screenWidth) + ".")

        if self.step == 0:
            self._world.staticEntities.append(self.ef.createBlock(0, self.currentHeight, screenWidth, 40))
            self._world.staticEntities.append(self.ef.createBlock(0, 0, 40, self.currentHeight))

        #         # generate flat world
        #         if self._world.seed == 0:
        #             staticEntities = [self.ef.createBlock(currentX, self.currentHeight, 2 * screenWidth, 40)]
        #             dynamicEntities = []
        #         # generate world from single slice
        #         if self._world.seed - 1 < len(worldSlices):
        #             staticEntities, dynamicEntities = worldSlices[self._world.seed - 1].generate(self)
        #         else:
        worldSlice = self._random.choice(worldSlices)
        staticEntities, dynamicEntities = worldSlice.generate(self)

        self._world.staticEntities.extend(staticEntities)
        self._world.dynamicEntities.extend(dynamicEntities)
        self.ef.cycle()
        self.generateEnemies([ent for ent in staticEntities if ent.isSolid()])
        self.step += 1

    #     def generateSlice0(self, currentX):
    #         for i in range(0, 18):
    #             value = int(self._random.random() * 3) - 1
    #             self.ef.createBlock(currentX + i * 120, self.currentHeight, 120, 40)
    #             self.currentHeight += value * 40
    #
    #     def generateSlice1(self, currentX):
    #         for i in range(0, 18):
    #             value = int(self._random.random() * 3) - 1
    #             if i % 3 != 0:
    #                 self.ef.createBlock(currentX + i * 120, self.currentHeight, 120, 40)
    #             self.currentHeight += value * 40

    def generateEnemies(self, solidEntities):
        # choose the number of livings to create
        maxLivings = int(math.sqrt(self.step))  # int(2 * (5 - math.exp((80 - self.step) / 50)))
        count = self._random.randint(0, maxLivings)
        for _ in range(count):
            # choose the block to create the living on
            entity = self._random.choice(solidEntities)
            # choose the x coordinate
            x = entity.getX() + self._random.randint(0, entity.getWidth())
            self._world.dynamicEntities.append(self.ef.createEnemy(x, entity.getY() - 40))
