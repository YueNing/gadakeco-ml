import pygame
from pygame.font import SysFont

import util.texturehandler as texhandler
from context.basecontext import BaseContext
from gui.guibutton import GuiButton
from lib import constants
from neat import networkrenderer
from neat.population import Population
from render.renderworld import RenderNeuronalWorld
from world import NeuronalWorld


class NNTraningContext(BaseContext):
    """
    Context for training neuronal networks
    """

    def __init__(self, seed, setContextFunc, population=None, train=True):
        BaseContext.__init__(self, setContextFunc)
        self.seed = seed
        self.pop = Population(seed, 100) if population is None else population
        if train:
            self.worlds = []
            for net in sorted(self.pop.current_generation, key=lambda x: x.fitness, reverse=True):
                nWorld = NeuronalWorld(self.pop.seed, net)
                nWorld.renderer = RenderNeuronalWorld(nWorld)
                self.worlds.append(nWorld)
                nWorld.generatePlatform()
        else:
            best_nn = max((n for n in self.pop.current_generation), key=lambda x: x.fitness)
            nWorld = NeuronalWorld(self.pop.seed, best_nn)
            nWorld.renderer = RenderNeuronalWorld(nWorld)
            self.worlds = [nWorld]
        self.drawmode = 0
        self._train = train

        # the gui overlays
        self._overlays = texhandler.adjustedSurface(texhandler.Textures.overlays, height=48)

        fontObj = SysFont("Monospace", 30, bold=True)
        # mode switch buttons
        self.addElements({
            "bNext": GuiButton(constants.screenWidth - 100, constants.screenHeight - 70, fontObj, "->",
                               width=70).connect(self.buttonModeSwitch, 1),
            "bPrevious": GuiButton(30, constants.screenHeight - 70, fontObj, "<-", width=70).connect(
                self.buttonModeSwitch, -1)
        })

    def calculateDelta(self, clock):
        if self._train:
            return constants.UPS
        else:
            return BaseContext.calculateDelta(self, clock)

    def update(self, t):
        BaseContext.update(self, t)

        done = True
        for world in self.worlds:
            if world.update(constants.UPS):
                done = False

        if done and self._train:
            self.pop.save_to_file(constants.res_loc("networks") + self.pop.name + ".pop")
            self.pop.create_next_generation()
            self.pop.generation_count += 1

            self.worlds = []
            for net in self.pop.current_generation:
                nWorld = NeuronalWorld(self.pop.seed, net)
                nWorld.renderer = RenderNeuronalWorld(nWorld)
                self.worlds.append(nWorld)
                nWorld.generatePlatform()

    def draw(self, screen):
        if self.worlds:
            [self.drawSimple, self.drawNetwork, self.drawSummary, self.drawOverview][self.drawmode](screen)
        BaseContext.draw(self, screen)
        # draw current generation
        renderedGen = SysFont("Monospace", 40, bold=True).render(str(self.pop.generation_count), 1, (50, 50, 50))
        # draw generation overlay (dinosaur egg)
        screen.blit(self._overlays, (485, 650), (336, 0, 48, 48))
        screen.blit(renderedGen, (540, 655))

    def drawSimple(self, screen):
        """
        only draws the first network
        """
        self.worlds[0].renderer.render(screen)

    def drawNetwork(self, screen):
        """
        draws the first network with it's network-graph
        """
        #        world = max(self.worlds, key=lambda w: w.nn.fitness)
        # draw the world
        world = self.worlds[0]
        world.renderer.render(screen)

        networkSurface = pygame.Surface((750, 180)).convert_alpha()
        networkSurface.fill((0, 0, 0, 0))
        # draw the minimap and network
        networkrenderer.render_network(networkSurface, world.nn, world.minimapValues)
        screen.blit(networkSurface, (10, 60))

    def drawSummary(self, screen):
        """
        draws a summary
        """
        x = 30
        y = 50
        fontObj = SysFont("Monospace", 18, bold=True)

        time = 0
        rowHeight = fontObj.get_height() + 2

        for world in self.worlds:
            time = max(time, world.time)
            renderedFitness = fontObj.render("Fitness: {0:.2f}".format(world.nn.fitness), 1, (255, 255, 255))

            if (y + rowHeight > (constants.screenHeight - 95)):
                y = 50
                x += 260
                if x + renderedFitness.get_width() > constants.screenWidth:
                    break
                # draw vertical line
                pygame.draw.line(screen, (100, 100, 100), (x - 10, 45), (x - 10, constants.screenHeight - 100), 2)
            # draw horizontal line (if still on first column)
            elif x < 100:
                pygame.draw.line(screen, (100, 100, 100), (25, y + rowHeight - 3),
                                 (constants.screenWidth - 25, y + rowHeight - 3), 2)

            screen.blit(renderedFitness, (x, y))

            y += rowHeight

        # draw the time
        renderedTime = pygame.font.SysFont("Monospace", 34, bold=True).render("Time: {0:.2f}".format(time), 1,
                                                                              (255, 255, 255))
        screen.blit(renderedTime, ((constants.screenWidth - renderedTime.get_width()) // 2, 10))

    def drawOverview(self, screen):
        """
        draws the best 9 networks
        """
        if len(self.worlds) >= 9:
            partWidth = constants.screenWidth // 3
            partHeight = constants.screenHeight // 3
            bestWords = sorted(self.worlds, key=lambda x: -x.nn.fitness)[:9]
            for y in range(0, 3):
                for x in range(0, 3):
                    surface = pygame.Surface(constants.screenSize)
                    bestWords[3 * y + x].renderer.render(surface)
                    surface = pygame.transform.scale(surface, (partWidth, partHeight))
                    screen.blit(surface, (partWidth * x, partHeight * y))
                    pygame.draw.rect(screen, (0, 0, 0), (partWidth * x, partHeight * y, partWidth, partHeight), 1)
        else:
            self.drawSimple(screen)

    def handleEvent(self, event):
        if BaseContext.handleEvent(self, event):
            return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                from context.gamepausecontext import GamePauseContext
                self._setContextFunc(GamePauseContext(self, self._setContextFunc))
            elif event.key == pygame.K_TAB:
                self.drawmode = (self.drawmode + 1) % 4
        return False

    """
    button functions
    """

    def buttonModeSwitch(self, inc):
        self.drawmode = (self.drawmode + inc) % 4
