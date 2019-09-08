from lib.constants import screenWidth, screenHeight

cameraPosX = 0.4
cameraPosY = 0.6


class Camera:
    """
    camera for rendering
    """

    def __init__(self, player):
        self._player = player
        self._x = self._player.getMidX() - screenWidth * cameraPosX
        self._y = self._player.getMidY() - screenHeight * cameraPosY

    def setPosition(self, x, y):
        self._x = x
        self._y = y

    def update(self, sElapsed):
        destX = self._player.getMidX() - screenWidth * cameraPosX
        destY = self._player.getMidY() - screenHeight * cameraPosY
        # TODO: maybe better following algorithm
        self._x += (destX - self._x) * 4 * sElapsed
        self._y += (destY - self._y) * 4 * sElapsed

    def getX(self):
        return self._x

    def getY(self):
        return self._y
