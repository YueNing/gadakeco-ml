import random

import pygame
from pygame.font import Font

from context.basecontext import BaseContext
from gui.guibutton import GuiButton
from gui.guicontainer import GuiContainer
from gui.guilabel import GuiLabel
from gui.guiscrollbar import GuiScrollbar
from lib import config
from lib.constants import screenSize
from util import texturehandler
from util.soundhandler import Music


class OptionContext(BaseContext):
    """
    Context for the options screen
    """

    def __init__(self, parent, setContextFunc):
        BaseContext.__init__(self, setContextFunc)
        self._parent = parent
        self._background = texturehandler.fillSurface(pygame.Surface(screenSize), random.choice(texturehandler.blocks),
                                                      (64, 64))

        fontObj = Font(None, 40)
        self.addElements({
            "lCaption": GuiLabel.createCentered(10, Font(None, 60), "Options"),
            "cEntries": GuiContainer(240, 77, 600, 450, fontObj),
            "bRestoreDefaults": GuiButton(390, 580, fontObj, "Restore Defaults", width=300).connect(
                self.buttonRestoreDefaults),
            "bBack": GuiButton(240, 650, fontObj, "Cancel", width=285).connect(self.buttonBack),
            "bSave": GuiButton(555, 650, fontObj, "Save", width=285).connect(self.buttonSave)
        })

        # add config Entry buttons
        y = 10
        for entry in config.Entries:
            self._elements["cEntries"].addElement("l" + entry.name, GuiLabel(50, y + 16, fontObj, entry.desc + ":"))

            if entry.entryType == config.EntryType.Key or entry.entryType == config.EntryType.Toggle:
                self._elements["cEntries"].addElement("b" + entry.name,
                                                      GuiButton(300, y, fontObj, str(entry), width=200).connect(
                                                          self.buttonConfigEntry, entry))
            elif entry.entryType == config.EntryType.Scroll:
                self._elements["cEntries"].addElement("b" + entry.name, GuiScrollbar(300, y + 5, 200, 40, fontObj,
                                                                                     value=entry.getCurrentValue(),
                                                                                     barLength=20).connect(
                    self.scrollConfigEntry, entry))
            y += 70

    def draw(self, screen):
        screen.blit(self._background, (0, 0))
        BaseContext.draw(self, screen)

    """
    button press functions
    """

    def buttonConfigEntry(self, entry):
        button = self._elements["cEntries"]["b" + entry.name]

        if entry.entryType == config.EntryType.Key:
            button.setText("Press Key")
            # redraw
            self.draw(pygame.display.get_surface())
            pygame.display.update(button.getRect())

            event = pygame.event.wait()
            while event.type != pygame.KEYDOWN:
                if event.type == pygame.QUIT:
                    self.closeApp()
                else:
                    event = pygame.event.wait()

            entry.setCurrentValue(event.key)
            button.setText(pygame.key.name(event.key).capitalize())

        elif entry.entryType == config.EntryType.Toggle:
            value = not entry.getCurrentValue()
            entry.setCurrentValue(value)
            button.setText(str(value))

    def scrollConfigEntry(self, entry):
        value = self._elements['cEntries']["b" + entry.name].getValue()
        entry.setCurrentValue(value)

    def buttonRestoreDefaults(self):
        config.resetConfig()
        for entry in config.Entries:
            self._elements['cEntries']["b" + entry.name].setText(str(entry))

    def buttonBack(self):
        # restore last saved configs
        config.loadConfig()
        self._setContextFunc(self._parent)

    def buttonSave(self):
        config.saveConfig()
        Music.setVolume(config.Entries.MusicVolume.getCurrentValue())
        self._setContextFunc(self._parent)
