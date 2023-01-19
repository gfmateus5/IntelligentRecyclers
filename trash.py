import pygame

from macros import *
from calculations import Position
from abc import ABC


class Trash(pygame.sprite.Sprite, ABC):

    def __init__(self, simulation, x, y):
        super().__init__()
        self.simulation = simulation
        self.image = pygame.image.load("trash.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (16, 16))
        self.weight = 1
        self.rect = self.image.get_rect()
        self.point = Position(x, y)
        self.rect.center = [int((self.point.x * SIZE_OF_TILE) + X_MARGIN), int((self.point.y * SIZE_OF_TILE) + Y_MARGIN)]
