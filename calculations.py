import random
from dataclasses import dataclass
from enum import Enum


class Direction(Enum):
    East = 1
    West = 2
    North = 3
    South = 4


def random_direction():
    return random.choice([Direction.South, Direction.North, Direction.West, Direction.East])

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None
        self.h_Cost = 0
        self.g_Cost = 0
        self.f_Cost = 0

    def __repr__(self):
        return str((self.x, self.y))

    def calculate_g_cost(self, neighbour):
        point = Position(self.x, self.y)
        return distance_between_points(point, Position(neighbour.x, neighbour.y))

    def calculate_h_cost(self, endPoint):
        point = Position(self.x, self.y)
        return distance_between_points(point, Position(endPoint.x, endPoint.y))

    def calculate_f_cost(self):
        self.f_Cost = self.g_Cost + self.h_Cost


# simplifying our work to define the class Position
@dataclass(order=True, repr=True, frozen=True)
class Position:
    x: int
    y: int

    def a_Star_search(self, endpoint, simulation):

        my_sector = None
        end_sector = None
        for sector in simulation.sectors:
            if Position(self.x, self.y) in sector.sector_tiles:
                my_sector = sector
            if Position(endpoint.x, endpoint.y) in sector.sector_tiles:
                end_sector = sector

        start = Node(self.x, self.y)

        end = Node(endpoint.x, endpoint.y)

        open_set = []
        closed_set = []
        open_set.append(start)

        while len(open_set) > 0:
            current = open_set[0]

            for i in range(1, len(open_set)):
                if open_set[i].f_Cost < current.f_Cost or (
                        open_set[i].f_Cost == current.f_Cost and open_set[i].h_Cost < current.h_Cost):
                    current = open_set[i]
            open_set.remove(current)
            closed_set.append(current)
            if current.x == end.x and current.y == end.y:
                return self.obtainPath(current, simulation, my_sector, end_sector)

            for neighbour in self.getNeighbours(current, simulation, my_sector, end_sector):
                walkable = simulation.isWalkable(neighbour, start, my_sector, end_sector)
                if walkable == "Container" or neighbour in closed_set:
                    continue

                if walkable == "Detector":
                    if neighbour.x == end.x and neighbour.y == end.y:
                        return []
                    continue

                costToNeighbour = current.g_Cost + current.calculate_g_cost(neighbour)
                if (costToNeighbour < neighbour.g_Cost) or neighbour not in open_set:
                    neighbour.g_Cost = costToNeighbour
                    neighbour.h_Cost = neighbour.calculate_h_cost(end)
                    neighbour.f_Cost = neighbour.h_Cost + neighbour.g_Cost
                    neighbour.parent = current
                    if neighbour not in open_set:
                        open_set.append(neighbour)

    def getNeighbours(self, current, simulation, my_sector, end_sector):
        neighbours = []
        positions = [-1, 0, 1]
        for i in positions:
            for j in positions:
                posX = current.x + i
                posY = current.y + j

                if 0 < posX < 60 and 0 < posY < 32 and abs(i) + abs(j) == 1:
                    neighbours.append(Node(posX, posY))
        return neighbours

    def obtainPath(self, current, simulation, my_sector, end_sector):
        points = []
        start = Node(self.x, self.y)
        while current.x != start.x or current.y != start.y:
            points.append(Position(current.x, current.y))
            current = current.parent
        points.append(Position(current.x, current.y))
        return points[::-1]


def distance_between_points(origin: Position, destiny: Position):
    distance_x = abs(destiny.x - origin.x)
    distance_y = abs(destiny.y - origin.y)

    return distance_x + distance_y


