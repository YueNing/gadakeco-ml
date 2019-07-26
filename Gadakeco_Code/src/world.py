import lib.constants as const
from camera import Camera, cameraPosX
from entity.entityplayer import EntityPlayer
from worldgeneration.worldgen import WorldGen


class World:
    """
    the world class
    """

    def __init__(self, seed):
        # the gravity-strength of this world
        self.gravity = 9.81
        # the total world time
        self.time = 0.0
        self.lastT = 0

        # entities
        self.player = EntityPlayer(self, 480, (640 - 80) - 40)
        self.camera = Camera(self.player)
        self.staticEntities = []
        self.dynamicEntities = []
        self.visibleStaticEntities = []
        self.visibleDynamicEntities = []

        # worldgen stuff
        self.seed = seed
        self.furthestX = 0
        self.worldgen = WorldGen(self)
        self.points = 0

    def generatePlatform(self):
        # generate the starting platform
        self.worldgen.generateWorldSlice()

    def update(self, t):
        self.time += t

        self.visibleStaticEntities = [ent for ent in self.staticEntities if ent.isVisible(self.player)]
        self.visibleDynamicEntities.clear()
        temp = []
        # sort the visible entities into the list and move them
        for ent in self.dynamicEntities:
            if ent.isAlive() and ent.isVisible(self.player):
                self.visibleDynamicEntities.append(ent)
                # (calculation was done last frame, so we have to use the last t here)
                ent.move(self.lastT)
            else:
                temp.append(ent)
        # move the player (calculation was done last frame, so we have to use the last t here)
        self.player.move(self.lastT)

        # update entities (collision detection/resolve)
        for ent in self.visibleDynamicEntities:
            if ent.updateAndIsAlive(self, t):
                temp.append(ent)
        # update player
        isAlive = self.player.updateAndIsAlive(self, t)
        # update the camera
        self.camera.update(t)
        # update points
        if not self.player._inAir and self.player.getX() > self.furthestX:
            self.points += self.player.getX() - self.furthestX
            self.furthestX = self.player.getX()
        # update inputs
        self.handleInput()
        # save current delta t for 'move' in the next frame
        self.lastT = t

        self.dynamicEntities = temp
        # create new world slice if needed
        if self.furthestX + cameraPosX * const.screenWidth > self.worldgen.step * 2048:
            self.worldgen.generateWorldSlice()

        return isAlive

    def handleInput(self):
        import pygame
        from lib.config import Entries

        inputs = [pygame.key.get_pressed()[Entries.KeyLeft.getCurrentValue()],
                  pygame.key.get_pressed()[Entries.KeyRight.getCurrentValue()],
                  pygame.key.get_pressed()[Entries.KeySpace.getCurrentValue()]]
        self.player.setInput(*inputs)


class NeuronalWorld(World):
    """
    a world for a single neuronal network
    """

    def __init__(self, seed, nn):
        World.__init__(self, seed)
        self.nn = nn
        self.lastTimePointsEarned = 0
        self.minimapValues = [0] * 18 * 27
        self._running = True

    def update(self, t):
        if not self._running:
            return False

        lastPoints = self.points
        self._running = World.update(self, t)
        if lastPoints < self.points:
            self.lastTimePointsEarned = self.time

        self.nn.update_fitness(self.points, self.time)

        if self._running:
            self._running = (self.time - self.lastTimePointsEarned <= 3.5)

        return self._running

    def handleInput(self):
        self.createMinimapValues()
        if self.points > 0:
            self.player.setInput(*self.nn.evaluate(self.minimapValues))

    def createMinimapValues(self):
        self.minimapValues = [0] * (18 * 27)

        for entity in self.visibleStaticEntities + self.visibleDynamicEntities:
            x, y = entity.getCamRelPos(self.camera)
            x, y = int(x) // 40, int(y) // 40
            tilesX = max(round(entity.getWidth() / 40), 1)
            tilesY = max(round(entity.getHeight() / 40), 1)
            for xx in range(x, x + tilesX):
                for yy in range(y, y + tilesY):
                    if 0 <= xx < 27 and 0 <= yy < 18:
                        self.minimapValues[yy * 27 + xx] = entity.getMinimapID()
