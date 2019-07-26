import sys
from math import inf as infinity

from util.directions import Direction


class AABB:
    """
    an entity's bounding box ((x, y) is the upper left corner)
    """

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def move(self, x, y):
        self.x += x
        self.y += y

    def intersects(self, other):
        """
        checks if this and another AABB intersect
        """
        return ((self.x < other.x + other.width) and (other.x < self.x + self.width)  # horizontal intersection
                and (self.y < other.y + other.height) and (other.y < self.y + self.height))  # vertical intersection

    def contains(self, x, y):
        """
        checks if the given point lies within this AABB
        """
        return (self.x < x < self.x + self.width) and (self.y < y < self.y + self.height)

    def getOverlapArea(self, other):
        """
        calculates the overlapping area of this and the other AABB (only correct if the AABBs are colliding)
        """
        oWidth = min(self.x + self.width, other.x + other.width) - max(self.x, other.x)
        oHeight = min(self.y + self.height, other.y + other.height) - max(self.y, other.y)
        return oWidth * oHeight

    def slide(self, lastX, lastY, dX, dY, entryTime, direction):
        self.x = lastX + dX * entryTime
        self.y = lastY + dY * entryTime

        dot = (dX * direction.y() + dY * direction.x()) * (1.0 - entryTime - sys.float_info.epsilon)
        dXSlide = dot * direction.y()
        dYSlide = dot * direction.x()
        self.move(dXSlide, dYSlide)

        #         dXges = self.x - lastX
        #         dYges = self.y - lastY
        dXges = dXSlide + dX * abs(direction.y()) * entryTime
        dYges = dYSlide + dY * abs(direction.x()) * entryTime

        return dXges, dYges

    def collisionResponse(self, lastX, lastY, other, responsefunc=slide):
        """
        calculates the appropriate collision response for this AABB's EntityLiving
        """
        dX = self.x - lastX
        dY = self.y - lastY

        # entity moved right
        if dX > 0:
            xDistEntry = other.x - (lastX + self.width)
        # entity moved left
        else:
            xDistEntry = (other.x + other.width) - lastX
        # entity moved up
        if dY < 0:
            yDistEntry = (other.y + other.height) - lastY
        # entity moved down
        else:
            yDistEntry = other.y - (lastY + self.height)

        # find time of collision for each axis
        if dX == 0:
            xEntryTime = -infinity
        else:
            xEntryTime = xDistEntry / dX
        if dY == 0:
            yEntryTime = -infinity
        else:
            yEntryTime = yDistEntry / dY

        # find the earliest times of collision
        entryTime = max(xEntryTime, yEntryTime) - sys.float_info.epsilon

        # didn't move
        if (xEntryTime < 0 and yEntryTime < 0) or xEntryTime > 1 or yEntryTime > 1:
            direction = Direction.invalid
            entryTime = 1.0
        else:
            # collided on y-axis (in x-direction) first
            if xEntryTime > yEntryTime:
                if xDistEntry < 0:
                    direction = Direction.right
                else:
                    direction = Direction.left
            # collided on x-axis (in y-direction) first
            else:
                if yDistEntry < 0:
                    direction = Direction.down
                else:
                    direction = Direction.up

        # execute response
        if responsefunc is not None:
            dX, dY = responsefunc(self, lastX, lastY, dX, dY, entryTime, direction)
            return dX, dY, direction
        else:
            return direction

    def __str__(self):
        return "X: " + str(self.x) + ", Y: " + str(self.y) + ", width: " + str(self.width) + ", height: " + str(
            self.height)
