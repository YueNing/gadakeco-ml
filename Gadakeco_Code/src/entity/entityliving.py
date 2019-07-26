import sys

import lib.constants as const
from camera import cameraPosX, cameraPosY
from entity.entitybase import EntityBase


class EntityLiving(EntityBase):
    """
    a living entity
    """

    def __init__(self, x, y, width, height):
        EntityBase.__init__(self, x, y, width, height)
        # movement data
        self._lastX = x
        self._lastY = y
        self._velocityX = 0
        self._velocityY = 0
        self._accelerationX = 0
        self._accelerationY = 0
        self._lastAccelerationX = 0
        self._lastAccelerationY = 0
        # live state of the entity (e.g. -1 = dead)
        self.state = 0

    # id for the neuronalnetwork data
    def getMinimapID(self):
        return -1

    def getLastX(self):
        return self._lastX

    def getLastY(self):
        return self._lastY

    def isVisible(self, player):
        horizontal = (
                                 self.getX() + self.getWidth() + const.dynamicUpdateDist * const.screenWidth * cameraPosX >= player.getX()) and (
                                 self.getX() - const.dynamicUpdateDist * const.screenWidth * (
                                     1.0 - cameraPosX) <= player.getX() + player.getWidth())
        vertical = (
                               self.getY() + self.getHeight() + const.dynamicUpdateDist * const.screenHeight * cameraPosY >= player.getY()) and (
                               self.getY() - const.dynamicUpdateDist * const.screenHeight * (
                                   1.0 - cameraPosY) <= player.getY() + player.getHeight())
        return horizontal and vertical

    def move(self, t):
        '''
        movement
        '''
        self._lastX = self.getX()
        self._lastY = self.getY()

        self._lastAccelerationX = self._accelerationX
        self._lastAccelerationY = self._accelerationY

        # calculate velocity from acceleration according to Velocity Verlet integration (continued in updateVelocity())
        dX = self._velocityX * t + (0.5 * self._accelerationX * t * t)
        dY = self._velocityY * t + (0.5 * self._accelerationY * t * t)

        # times 100 because the math assumes meters but we're assuming 1 cm per pixel, so we need to scale the results
        self._aabb.move(100.0 * dX, 100.0 * dY)
        # reset acceleration
        self._accelerationX = 0
        self._accelerationY = 0

    def isAlive(self):
        return self.state != -1

    def updateAndIsAlive(self, world, t):
        '''
        collision detection and resolve
        '''
        # again because we assume meters for the math but 1cm per pixel this has to be multiplied by 100
        t_ = max(sys.float_info.epsilon, t) * 100.0
        # some terms for calculations
        addInvX = 0.5 * self._lastAccelerationX * t
        addInvY = 0.5 * self._lastAccelerationY * t

        collisionStack = []
        while True:
            collidedEntities = []

            for ent in world.visibleStaticEntities:
                if not ent.isSolid():
                    if self.isColliding(ent):
                        direction = self._aabb.collisionResponse(self._lastX, self._lastY, ent._aabb, None)
                        self.onCollideStatic(ent, direction, world)
                elif self.isColliding(ent) and ent not in collisionStack:
                    collidedEntities.append(ent)

            # no more collisions
            if not collidedEntities:
                break

            # sort the collided entities by the overlapping area (from high to low) and resolve collision in the highest one
            toResolve = max(collidedEntities, key=self.getOverlappingArea)
            collisionStack.append(toResolve)

            # perform collision response
            dX, dY, direction = self._aabb.collisionResponse(self._lastX, self._lastY, toResolve._aabb)
            # reverse calculate the velocity
            self._velocityX = dX / t_ - addInvX
            self._velocityY = dY / t_ - addInvY
            # notify collision
            self.onCollideStatic(toResolve, direction, world)

        for ent in world.visibleDynamicEntities:
            if ent != self:
                if self.isColliding(ent):
                    direction = self._aabb.collisionResponse(self._lastX, self._lastY, ent._aabb, None)
                    self.onCollide(ent, direction, world)

        self.updateVelocity(world, t)

        return self.isAlive()

    def updateVelocity(self, world, t):
        """
        updates and recalculates the velocity
        """
        self._accelerationY += world.gravity

        # finish Velocity Verlet integration
        avgAccelerationX = (self._lastAccelerationX + self._accelerationX) / 2.0
        avgAccelerationY = (self._lastAccelerationY + self._accelerationY) / 2.0
        self._velocityX += avgAccelerationX * t
        self._velocityY += avgAccelerationY * t

    def onCollide(self, livingEntity, side, world):
        """
        what should happen if self collided with 'livingEntity' on 'side'
        """
        pass

    def onCollideStatic(self, entityBase, side, world):
        """
        what should happen if self collided on the 'side' of 'entityBase'
        """
        pass

    def __str__(self):
        return "EntityLiving at {};\t lastX={},\t lastY={};\t velocity={}".format(self._aabb, self._lastX, self._lastY,
                                                                                  (self._velocityX, self._velocityY))
