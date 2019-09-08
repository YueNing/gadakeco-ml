import os

# the name of the game
GAME_NAME = "Gadakeco"
screenSize = screenWidth, screenHeight = 1080, 720
# the desired framerate
FPS = 30
MAX_DELTA = 1.5 / FPS
# constant frametime for physic updates (Updates Per Second)
UPS = 0.035
# maximum number of physics updates per game loop iteration
MAX_UPDATES = 10

# distances for when entities should be "visible" (in multiples of screenWidth)
staticUpdateDist = 1.5
dynamicUpdateDist = 1.3

_RES_LOC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "res")) + os.path.sep


def res_loc(subfolder=None):
    if subfolder:
        path = _RES_LOC + subfolder + os.path.sep
    else:
        path = _RES_LOC

    # ensure the directory exists
    if not os.path.exists(path):
        os.makedirs(path)

    return path
