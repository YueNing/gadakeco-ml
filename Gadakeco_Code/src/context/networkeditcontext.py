import os
import random

import pygame
from pygame.font import Font, SysFont

from context.basecontext import BaseContext
from gui.guibutton import GuiButton
from gui.guilabel import GuiLabel
from gui.guitextfield import GuiNumberTextfield
from lib import constants
from neat.population import Population
from util import texturehandler
from util.soundhandler import Music


class NetworkEditContext(BaseContext):
    """
    context for viewing/editing a saved neuronal network
    """

    def __init__(self, networkContext, setContextFunc, popFileName):
        BaseContext.__init__(self, setContextFunc)
        self._networkContext = networkContext
        self._popFileName = popFileName
        self._pop = Population.load_from_file(constants.res_loc("networks") + popFileName)

        self._background = texturehandler.fillSurface(pygame.Surface(constants.screenSize),
                                                      random.choice(texturehandler.blocks), (64, 64))

        best_fitness = max(n.fitness for n in self._pop.current_generation)
        fontObj = Font(None, 40)
        self.addElements({
            "lCaption": GuiLabel.createCentered(10, Font(None, 60), self._pop.name),
            "lSeed": GuiLabel(240, 90, fontObj, "Current seed:"),
            "tfSeed": GuiNumberTextfield(450, 87, SysFont("Monospace", 24, bold=True), width=140,
                                         text=str(self._pop.seed)),
            "bSeed": GuiButton(600, 87, fontObj, "Set Seed", width=200, height=32).connect(self.buttonSetSeed),
            "lSize": GuiLabel(240, 130, fontObj, "Population size: {}".format(len(self._pop.current_generation))),
            "lFitness": GuiLabel(240, 170, fontObj, "Highest fitness: {0:.2f}".format(best_fitness)),
            "lGeneration": GuiLabel(240, 210, fontObj, "Generation: {}".format(self._pop.generation_count)),
            "bDelete": GuiButton(390, 470, fontObj, "Delete (hold CTRL)", width=300, height=40,
                                 startColor=(255, 50, 50), endColor=(255, 100, 100)).connect(self.buttonDelete),
            "bShowResult": GuiButton(240, 530, fontObj, "Show Result", width=285).connect(self.buttonShowResult),
            "bResumeTraining": GuiButton(555, 530, fontObj, "Resume Training", width=285).connect(
                self.buttonResumeTraining),
            "bBack": GuiButton(240, 600, fontObj, "Back").connect(self.buttonBack)
        })

        # enable key repeats
        pygame.key.set_repeat(500, 50)

    def draw(self, screen):
        screen.blit(self._background, (0, 0))
        BaseContext.draw(self, screen)

    def buttonSetSeed(self):
        seed = self._elements['tfSeed'].getText()
        if not seed or int(seed) == self._pop.seed:
            return

        self._pop.seed = int(seed)

    #        self._pop.save_to_file(self._popFileName)

    def buttonDelete(self):
        # only allow action when CTRL is pressed to prevent deleting by mistake
        if pygame.key.get_mods() & pygame.KMOD_CTRL:
            try:
                os.remove(constants.res_loc("networks") + self._popFileName)
                # update entries in network container
                self._networkContext.updateNetworks()
                self._setContextFunc(self._networkContext)
            except:
                print("couldn't remove '{}'".format(constants.res_loc("networks") + self._popFileName))

    def buttonShowResult(self):
        from context.networktrainingcontext import NNTraningContext
        Music.stop()
        self._setContextFunc(NNTraningContext(0, self._setContextFunc, self._pop, False))

    def buttonBack(self):
        self._setContextFunc(self._networkContext)

    def buttonResumeTraining(self):
        from context.networktrainingcontext import NNTraningContext
        Music.stop()
        self._setContextFunc(NNTraningContext(0, self._setContextFunc, self._pop))
