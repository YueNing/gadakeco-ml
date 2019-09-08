import pygame
from pygame.locals import DOUBLEBUF, HWSURFACE

from lib import config
from lib.constants import GAME_NAME, screenSize, UPS, MAX_UPDATES

screen = None
context = None


def setContext(newContext):
    global context
    context = newContext


def init():
    global screen, context

    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode(screenSize, HWSURFACE | DOUBLEBUF)
    pygame.display.set_caption(GAME_NAME)

    # initializing texture- and soundhandler by importing them
    # initialize config
    config.init()
    # create current ContextManager
    from context.mainmenucontext import MainMenuContext
    context = MainMenuContext(setContext)


def main():
    init()
    print(GAME_NAME + " started")

    # activate the clock timer from pygame
    clock = pygame.time.Clock()
    # time accumulator
    accumulator = 0

    # game loop
    while True:
        sElapsed = context.calculateDelta(clock)
        # rendering "creates" delta-time, see https://gafferongames.com/post/fix_your_timestep/
        accumulator += sElapsed;

        # prevent "spiral of death"
        updateCount = 0
        while accumulator >= UPS:
            if updateCount >= MAX_UPDATES:
                accumulator = 0
                break
            updateCount += 1

            # update the context with constant delta t
            context.update(UPS)
            # physic updates "consume" delta-time
            accumulator -= UPS

        # TODO: interpolate between render-states

        # reset screen
        screen.fill((0, 0, 0))
        # drawing
        context.draw(screen)
        pygame.display.update()

        # debug


#         pygame.time.delay(1000)

if __name__ == '__main__':
    main()
