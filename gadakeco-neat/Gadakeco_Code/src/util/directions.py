from enum import Enum


class Direction(Enum):
    invalid = (0.0, 0.0)
    up = (0.0, -1.0)
    down = (0.0, 1.0)
    left = (-1.0, 0.0)
    right = (1.0, 0.0)

    def x(self):
        return self.value[0]

    def y(self):
        return self.value[1]

    def __str__(self):
        return str(self.value)
