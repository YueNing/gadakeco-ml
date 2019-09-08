import pygame

from gui import guiscrollbar
from gui.guielement import GuiElement


class CategoryData():
    def __init__(self, fontObj, *categories):
        self.fontObj = fontObj
        self._categoryMap = {category: i for i, category in enumerate(categories)}
        self._categories = tuple(fontObj.render(category, 1, (255, 255, 255)) for category in categories)
        self._weights = [1.0] * len(self._categories)
        self._sortReverse = [False] * len(self._categories)
        self._formatStrings = ["{}"] * len(self._categories)
        self._alignment = ["l"] * len(self._categories)

    def getCategories(self):
        return self._categories

    def setWeight(self, category, weight):
        if type(category) == int:
            self._weights[category] = weight
        else:
            self._weights[self._categoryMap[category]] = weight

    def getWeightedWidth(self, index, width):
        return width * self._weights[index] / sum(self._weights, 0)

    def getWeightedOffset(self, index, width):
        return width * sum(self._weights[:index]) / sum(self._weights, 0)

    def setDefaultSortDir(self, category, reverse):
        if type(category) == int:
            self._sortReverse[category] = reverse
        else:
            self._sortReverse[self._categoryMap[category]] = reverse

    def getDefaultSortDir(self, index):
        return self._sortReverse[index]

    def setFormatString(self, category, formatStr):
        if type(category) == int:
            self._sortReverse[category] = formatStr
        else:
            self._formatStrings[self._categoryMap[category]] = formatStr

    def getFormatString(self, index):
        return self._formatStrings[index]

    def setAlignment(self, category, alignment):
        if type(category) == int:
            self._alignment[category] = alignment
        else:
            self._alignment[self._categoryMap[category]] = alignment

    def getAlignment(self, index):
        return self._alignment[index]

    def __len__(self):
        return len(self._categories)


class GuiTable(GuiElement):
    """
    a gui table class
    """

    def __init__(self, x, y, width, height, fontObj, categoryData):
        GuiElement.__init__(self, x, y, width, height, fontObj)
        self._categoryData = categoryData
        self._rows = []
        self._spacing = 5
        self._scrollBar = guiscrollbar.GuiScrollbar(x + width - 30, y, 30, height, fontObj,
                                                    orientation=guiscrollbar.VERTICAL)
        self._clipRect = pygame.Rect(x, y + self._fontObj.get_height() + self._spacing,
                                     width - self._scrollBar.getWidth(),
                                     height - (self._fontObj.get_height() + self._spacing))
        self.setEventTypes(pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION)

        self._sortIndex = 0
        self._sortReverse = False

    def addRow(self, *row):
        if len(row) == len(self._categoryData):
            self._rows.append(row)
        else:
            print("row length does not match number of columns, input: ", row)

    def clear(self):
        self._rows.clear()

    def setSortIndex(self, index):
        self._sortIndex = index

    def sortRows(self):
        sortReverse = self._categoryData.getDefaultSortDir(self._sortIndex) ^ self._sortReverse
        self._rows.sort(key=lambda row: row[self._sortIndex], reverse=sortReverse)

    def update(self, t):
        self._scrollBar.update(t)

    def handleEvent(self, event):
        # scrolling with mouse wheel
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._aabb.contains(*event.pos) and (event.button == 4 or event.button == 5):
                scrollAmount = self.getHeight() / ((self._fontObj.get_height() + self._spacing) * (1 + len(self._rows)))
                scrollAmount = scrollAmount * scrollAmount
                if event.button == 4:
                    scrollAmount *= -1

                self._scrollBar.setValue(self._scrollBar.getValue() + scrollAmount)
                return True

            x = self.getX()
            for i in range(len(self._categoryData)):
                columnWidth = self._categoryData.getWeightedWidth(i, self.getWidth() - self._scrollBar.getWidth())
                if (x < event.pos[0] < x + columnWidth) and (
                        self.getY() < event.pos[1] < self.getY() + self._fontObj.get_height() + self._spacing):
                    if self._sortIndex == i:
                        self._sortReverse = not self._sortReverse
                    else:
                        self._sortIndex = i
                        self._sortReverse = False
                    self.sortRows()
                    return True
                x += columnWidth

        if self._scrollBar.canHandleEvent(event) and self._scrollBar.handleEvent(event):
            return True

        return False

    def draw(self, screen):
        screen.fill((70, 70, 70), self.getRect())

        x = self.getX()
        # draw the captions
        for i, category in enumerate(self._categoryData.getCategories()):
            columnWidth = self._categoryData.getWeightedWidth(i, self.getWidth() - self._scrollBar.getWidth())
            # draw vertical lines
            if i > 0:
                pygame.draw.line(screen, (0, 0, 0), (x, self.getY()), (x, self.getY() + self.getHeight()), 2)
            screen.blit(category, (x + (columnWidth - category.get_width()) / 2.0, self.getY() + 2))
            x += columnWidth

        # draw arrow for sorting direction
        x = self.getX() + self._categoryData.getWeightedOffset(self._sortIndex + 1,
                                                               self.getWidth() - self._scrollBar.getWidth()) - 20
        y = self.getY() + self._spacing
        if self._sortReverse:
            pygame.draw.polygon(screen, (200, 255, 200), (
            (x + 5, y), (x + 5, y + 12), (x, y + 12), (x + 6, y + 18), (x + 12, y + 12), (x + 7, y + 12), (x + 7, y)))
        else:
            pygame.draw.polygon(screen, (200, 255, 200), (
            (x + 7, y + 18), (x + 7, y + 6), (x + 12, y + 6), (x + 6, y), (x, y + 6), (x + 5, y + 6), (x + 5, y + 18)))
        # draw line
        y = self.getY() + self._fontObj.get_height() + self._spacing / 2.0
        pygame.draw.line(screen, (0, 0, 0), (self.getX(), y),
                         (self.getX() + self.getWidth() - self._scrollBar.getWidth(), y), 2)

        # draw entries
        screen.set_clip(self._clipRect)
        scrollHeight = max(((self._fontObj.get_height() + self._spacing) * (1 + len(self._rows))) - self.getHeight(), 0)

        y = 2 + self._categoryData.fontObj.get_height() + self._spacing - scrollHeight * self._scrollBar.getValue()
        for row in self._rows:
            if y > self.getHeight():
                break
            if y > 0:
                x = self.getX()
                for col, cell in enumerate(row):
                    columnWidth = self._categoryData.getWeightedWidth(col, self.getWidth() - self._scrollBar.getWidth())
                    valueStr = self._categoryData.getFormatString(col).format(cell)
                    renderedCell = self._fontObj.render(valueStr, 1, (255, 255, 255))

                    alignment = self._categoryData.getAlignment(col)
                    if alignment == "r":
                        screen.blit(renderedCell,
                                    (x + columnWidth - renderedCell.get_width() - self._spacing, self.getY() + y))
                    elif alignment == "c":
                        screen.blit(renderedCell, (x + (columnWidth - renderedCell.get_width()) // 2, self.getY() + y))
                    else:
                        screen.blit(renderedCell, (x + self._spacing, self.getY() + y))

                    x += columnWidth

            # draw horizontal lines
            pygame.draw.line(screen, (50, 50, 50), (self.getX(), self.getY() + y - self._spacing / 2.0), (
            self.getX() + self.getWidth() - self._scrollBar.getWidth(), self.getY() + y - self._spacing / 2.0), 1)
            y += self._fontObj.get_height() + self._spacing

        screen.set_clip()

        self._scrollBar.draw(screen)
