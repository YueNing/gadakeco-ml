import pygame

from gui.guielement import GuiElement


class GuiTextfield(GuiElement):
    """
    textfield for keyboard input
    """

    def __init__(self, x, y, fontObj, width=800, text=""):
        GuiElement.__init__(self, x, y, width, fontObj.get_height() + 4, fontObj)
        self._text = text
        self._hovered = False
        self._focused = False
        self._timer = 0
        self.setEventTypes(pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN)
        self._func = None

    def setFocused(self, focused):
        self._focused = focused

    def getFocused(self):
        return self._focused

    # connect this texfield to a on-changed function
    def connect(self, func):
        self._func = func
        return self

    def update(self, t):
        self._timer = (self._timer + t) % 2

        mouseX, mouseY = pygame.mouse.get_pos()
        if self._aabb.contains(mouseX, mouseY):
            self._hovered = True
        else:
            self._hovered = False

    def _isKeyValid(self, keyEvent):
        return keyEvent.key == pygame.K_BACKSPACE or keyEvent.unicode.isprintable()

    def handleEvent(self, event):
        # mouse event
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.setFocused(self._hovered)
            return self._hovered
        # keyboard event
        if event.type == pygame.KEYDOWN and self._focused and self._isKeyValid(event):
            if event.key == pygame.K_BACKSPACE:
                self._text = self._text[:-1]
            elif self._fontObj.size(self._text + event.unicode)[0] < self.getWidth() - 8:
                self._text += str(event.unicode)

            if self._func != None:
                self._func()
            return True
        else:
            return False

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), self.getRect())
        pygame.draw.rect(screen, (150, 150, 150), self.getRect(), 3)

        cursorOffset = 4
        if self._text:
            renderedText = self._fontObj.render(self._text, 1, (255, 255, 255))
            cursorOffset += renderedText.get_width()
            screen.blit(renderedText, (self.getX() + 4, self.getY() + 5))
        if self._focused and self._timer <= 1:
            pygame.draw.line(screen, (255, 255, 255), (self.getX() + cursorOffset, self.getY() + 4),
                             (self.getX() + cursorOffset, self.getY() + self.getHeight() - 4), 1)

    def getText(self):
        return self._text


class GuiNumberTextfield(GuiTextfield):
    def _isKeyValid(self, keyEvent):
        return keyEvent.key == pygame.K_BACKSPACE or keyEvent.unicode.isdigit()
