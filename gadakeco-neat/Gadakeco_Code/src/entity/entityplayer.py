from builtins import isinstance

from entity.entitycoin import EntityCoin
from entity.entityliving import EntityLiving
from util.directions import Direction

minVelocity = 0.15
maxVelocity = 4.0
deathYVelocity = 18.0
moveAcceleration = 5.0
# invulnerability time after being hit (in seconds)
invulTime = 3.0


class EntityPlayer(EntityLiving):
    """
    the player class
    """

    def __init__(self, world, x, y):
        EntityLiving.__init__(self, x, y, 38, 76)
        self._inAir = True
        self.leftDown = False
        self.rightDown = False
        self.jumpDown = False
        self.state = 2
        self.invulTimer = 0

        # for sounds
        self.jumped = False
        self.hurt = False
        self.falling = False

    def getMidX(self):
        return self.getX() + self.getWidth() / 2.0

    def getMidY(self):
        return self.getY() + self.getHeight() / 2.0

    def isVisible(self, player):
        return True

    def updateAndIsAlive(self, world, t):
        self._inAir = True
        if self._velocityY > deathYVelocity:
            self.state = -1
            self.falling = True
        self.invulTimer = max(self.invulTimer - t, 0)
        return EntityLiving.updateAndIsAlive(self, world, t)

    def updateVelocity(self, world, t):
        self.handleInput(world)
        # add "wind resistance"
        self._accelerationX -= 0.8 * self._velocityX
        # make slowing down faster (speed up deceleration)
        if self._accelerationX * self._velocityX < 0 and abs(self._accelerationX) < moveAcceleration / 2:
            self._accelerationX *= 4.0
        # update velocity based on acceleration
        EntityLiving.updateVelocity(self, world, t)

        if self._velocityX > minVelocity:
            self._velocityX = min(self._velocityX, maxVelocity)
        elif self._velocityX < -minVelocity:
            self._velocityX = max(self._velocityX, -maxVelocity)
        else:
            self._velocityX = 0

    def onCollide(self, livingEntity, side, world):
        # player collided with coin
        if isinstance(livingEntity, EntityCoin):
            world.points += 100
            livingEntity.state = -1
        # player collided with livingEntity from the top -> livingEntity is dead
        elif side == Direction.up:
            self._lastAccelerationY = 0
            self._accelerationY = -world.gravity * 20
            livingEntity.state = -1
            # add points (killing enemies is good)
            world.points += 100
        elif self.invulTimer == 0:
            self.invulTimer = invulTime
            # damage the player
            self.state -= 1
            self.hurt = True
            # subtract points (it's bad to get hurt)
            world.points -= 100

    def onCollideStatic(self, entityBase, side, world):
        if side == Direction.up:
            self._inAir = False

    def setInput(self, leftDown, rightDown, jumpDown):
        self.leftDown = leftDown
        self.rightDown = rightDown
        self.jumpDown = jumpDown

    def handleInput(self, world):
        if self.leftDown:
            self._accelerationX -= moveAcceleration
        if self.rightDown:
            self._accelerationX += moveAcceleration
        if self.jumpDown and not self._inAir:
            self._accelerationY = -world.gravity * 16.5
            self.jumped = True

    def __str__(self):
        return "EntityPlayer at " + str(self._aabb) + ";\t lastX=" + str(self._lastX) + ",\t lastY=" + str(
            self._lastY) + ";\t velocity=" + str((self._velocityX, self._velocityY))
