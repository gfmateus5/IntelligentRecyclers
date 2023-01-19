from tile import *
import random
from trash import *


class Sector:
    def __init__(self, topLeftPoint, simulation, number):
        self.topLeftPoint = topLeftPoint
        self.width = 20
        self.height = 16
        self.simulation = simulation
        self.range_for_spawn = []
        self.sector_number = number

        self.probability = 0
        self.totalTrashDetected = 0
        self.times_visited = 1
        self.trash_belief = 1000

        self.sector_tiles = {}
        self.setSectorTiles()
        self.isChosen = False

        beginningX = topLeftPoint[0] + 2
        beginningY = topLeftPoint[1] + 2

        self.sweep_points = [Position(beginningX, beginningY), Position(beginningX, beginningY + 11),
                             Position(beginningX + 5, beginningY + 11), Position(beginningX + 5, beginningY),
                             Position(beginningX + 10, beginningY), Position(beginningX + 10, beginningY + 11),
                             Position(beginningX + 15, beginningY + 11), Position(beginningX + 15, beginningY)]

        self.alternative_sweep_points = [Position(beginningX, beginningY + 11), Position(beginningX, beginningY),
                                         Position(beginningX + 5, beginningY), Position(beginningX + 5, beginningY + 11),
                                         Position(beginningX + 10, beginningY + 11), Position(beginningX + 10, beginningY),
                                         Position(beginningX + 15, beginningY), Position(beginningX + 15, beginningY + 11)]
        
        self.corners = [Position(beginningX, beginningY), Position(beginningX + 15, beginningY), Position(beginningX, beginningY + 11), Position(beginningX + 15, beginningY + 11)]

    def spawnTrash(self, quantity):
        for x in range(0, quantity):
            trash_list = self.obtainTrashList()
            point = random.choice(trash_list).point
            self.simulation.tile_dict[point].has_trash = True
            trash = Trash(self, point.x, point.y)
            self.simulation.trash_dict[point] = trash
            self.simulation.trash_group.add(trash)
            self.simulation.total_trash_spawned += 1

    def obtainTrashList(self):
        trash_list = []
        for x in self.sector_tiles.values():
            if x.__class__ == Park and not x.has_trash and x.point.x in range(1, 60) and x.point.y in range(1, 31):
                trash_list.append(x)

        return trash_list

    def setSectorTiles(self):
        for x in range(self.topLeftPoint[0], self.topLeftPoint[0] + self.width):
            for y in range(self.topLeftPoint[1], self.topLeftPoint[1] + self.height):
                self.sector_tiles[Position(x, y)] = self.simulation.tile_dict[Position(x, y)]
