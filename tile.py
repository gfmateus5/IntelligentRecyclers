import pygame

from macros import *
from abc import ABC
from calculations import Position


class Tile(pygame.sprite.Sprite, ABC):
    def __init__(self, simulation, x, y, color):
        super().__init__()
        self.simulation = simulation
        self.image = pygame.Surface((SIZE_OF_TILE, SIZE_OF_TILE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.point = Position(x, y)
        self.has_trash = False
        self.rect.center = [int((x * SIZE_OF_TILE) + X_MARGIN), int((y * SIZE_OF_TILE) + Y_MARGIN)]


class Park(Tile):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y, GREEN)


class Container(Tile):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y, BLUE)


class ContainerFieldOfView(Tile):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y, LIGHT_BLUE)


class Highlight(Tile):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y, ORANGE)
