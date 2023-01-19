import sys

import pygame
import random
from macros import *

from abc import ABC, abstractmethod
from calculations import Position, random_direction, distance_between_points
from tile import Container, ContainerFieldOfView, Highlight, Park
from calculations import Direction


class Robot(pygame.sprite.Sprite, ABC):
    def __init__(self, simulation, x, y, imagem):
        super().__init__()
        self.simulation = simulation
        self.image = pygame.image.load(imagem).convert()
        self.image = pygame.transform.scale(self.image, (16, 16))
        self.rect = self.image.get_rect()
        self.point = Position(x, y)
        self.rect.center = [int((self.point.x * SIZE_OF_TILE) + X_MARGIN),
                            int((self.point.y * SIZE_OF_TILE) + Y_MARGIN)]
        self.max_storage = 4
        self.has_in_storage = 0
        self.fov = self.current_fov()

    def move(self, point) -> None:

        self.point = point
        self.rect.center = [int((self.point.x * SIZE_OF_TILE) + X_MARGIN),
                            int((self.point.y * SIZE_OF_TILE) + Y_MARGIN)]
        self.fov = self.current_fov()
        return

    def canMove(self, point):

        robot_points = []
        for robot in self.simulation.robot_list:
            robot_points.append(robot.point)

        if point not in robot_points and self.simulation.tile_dict[point].__class__ != Container:
            return True

        return False

    def futurePoint(self, direction):

        point = self.point
        if direction == Direction.West:
            if self.point.x > 0:
                point = Position(self.point.x - 1, self.point.y)
        elif direction == Direction.East:
            if self.point.x < 59:
                point = Position(self.point.x + 1, self.point.y)
        elif direction == Direction.South:
            if self.point.y < 31:
                point = Position(self.point.x, self.point.y + 1)
        else:
            if self.point.y > 0:
                point = Position(self.point.x, self.point.y - 1)

        return point

    @abstractmethod
    def current_fov(self):
        pass

    @abstractmethod
    def decision(self):
        pass


class RandomCollector(Robot):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y, "c.png")
        self.direction = None
        self.number_of_steps = 0
        self.collected_trash = 0
        self.delivered_trash = 0

    def decision(self):
        if self.simulation.tile_dict[self.point].has_trash and self.has_in_storage < self.max_storage:
            self.simulation.tile_dict[self.point].has_trash = False
            trash = self.simulation.trash_dict[self.point]
            self.simulation.trash_group.remove(trash)
            self.simulation.trash_dict.pop(self.point)
            self.has_in_storage += 1
            self.collected_trash += 1
            self.simulation.trash_collected += 1
            print("Picked up trash")

        elif self.simulation.tile_dict[self.point].__class__ == ContainerFieldOfView and self.has_in_storage > 0:
            self.delivered_trash += self.has_in_storage
            self.simulation.trash_delivered += self.has_in_storage
            self.has_in_storage = 0
            print("Delivered to Container")

        else:
            self.direction = random_direction()
            if self.canMove(self.futurePoint(self.direction)):
                self.move(self.futurePoint(self.direction))
                self.number_of_steps += 1
                self.simulation.collector_number_of_steps += 1

    def current_fov(self):
        fov = []

        for y in range(self.point.y - 1, self.point.y + 2):
            for j in range(self.point.x - 1, self.point.x + 2):
                if (0 <= y <= 31) and (0 <= j <= 59):
                    fov.append(Position(j, y))
        return fov


class RobotSimpleReactiveCollector(Robot):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y, "c.png")
        self.direction = None
        self.path_to_follow = []
        self.number_of_steps = 0
        self.collected_trash = 0
        self.delivered_trash = 0

    def decision(self):

        for point in self.fov:
            if (self.simulation.tile_dict[point].has_trash and self.has_in_storage < self.max_storage and len(
                    self.path_to_follow) == 0) or (self.simulation.tile_dict[point].__class__ == ContainerFieldOfView and self.has_in_storage > 0 and len(self.path_to_follow) == 0):
                self.create_path(point)
                break

        if self.simulation.tile_dict[self.point].has_trash and self.has_in_storage < self.max_storage:
            self.simulation.tile_dict[self.point].has_trash = False
            trash = self.simulation.trash_dict[self.point]
            self.simulation.trash_group.remove(trash)
            self.simulation.trash_dict.pop(self.point)
            self.has_in_storage += 1
            self.path_to_follow = []
            self.collected_trash += 1
            self.simulation.trash_collected += 1
            print("Picked up trash")

        elif self.simulation.tile_dict[self.point].__class__ == ContainerFieldOfView and self.has_in_storage > 0:
            self.delivered_trash += self.has_in_storage
            self.simulation.trash_delivered += self.has_in_storage
            self.has_in_storage = 0
            self.path_to_follow = []
            print("Delivered to Container")

        elif len(self.path_to_follow) != 0:
            self.direction = self.path_to_follow[0]
            if self.canMove(self.futurePoint(self.direction)):
                self.path_to_follow.remove(self.path_to_follow[0])
                self.move(self.futurePoint(self.direction))
                self.number_of_steps += 1
                self.simulation.collector_number_of_steps += 1

        else:
            self.direction = random_direction()
            if self.canMove(self.futurePoint(self.direction)):
                self.move(self.futurePoint(self.direction))
                self.number_of_steps += 1
                self.simulation.collector_number_of_steps += 1

    def actions(self, points):
        for i in range(len(points) - 1):
            x_move = points[i].x - points[i + 1].x
            if x_move == 1:
                self.path_to_follow.append(Direction.West)
            elif x_move == -1:
                self.path_to_follow.append(Direction.East)

            y_move = points[i].y - points[i + 1].y
            if y_move == 1:
                self.path_to_follow.append(Direction.North)
            elif y_move == -1:
                self.path_to_follow.append(Direction.South)

    def create_path(self, point):
        self.path_to_follow = []
        points = self.point.a_Star_search(point, self.simulation)
        self.actions(points)

    def current_fov(self):
        fov = []

        for y in range(self.point.y - 1, self.point.y + 2):
            for j in range(self.point.x - 1, self.point.x + 2):
                if (0 <= y <= 31) and (0 <= j <= 59):
                    fov.append(Position(j, y))
        return fov


class RobotSimpleReactiveDetector(Robot):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y, "de.png")
        self.changing_points = [Position(x, y), Position(x, y + 27), Position(x + 5, y + 27), Position(x + 5, y), Position(x + 10, y),
                                Position(x + 10, y + 27), Position(x + 15, y + 27), Position(x + 15, y), Position(x + 20, y), Position(x + 20, y + 27), Position(x + 25, y + 27), Position(x + 25, y)]
        self.currentPosition = 0
        self.direction = None
        self.reversing = False
        self.path_to_follow = []
        self.number_of_steps = 0
        self.detected_trash = 0

    def decision(self) -> None:

        for point in self.fov:
            if self.simulation.tile_dict[point].has_trash and point not in self.simulation.detected_trash:
                self.simulation.detected_trash[point] = self.simulation.trash_dict[point]
                self.simulation.trash_to_be_assigned[point] = self.simulation.trash_dict[point]
                self.detected_trash += 1
                self.simulation.total_detected_trash += 1

        if len(self.path_to_follow) == 0 and not self.reversing and self.currentPosition != len(
                self.changing_points) - 1:
            self.currentPosition += 1
            self.create_path(self.changing_points[self.currentPosition])
            if len(self.path_to_follow) > 0:
                self.path_to_follow.remove(self.path_to_follow[0])
                self.move(self.futurePoint(self.direction))
                self.number_of_steps += 1
                self.simulation.detector_number_of_steps += 1

        elif len(self.path_to_follow) == 0 and self.reversing and self.currentPosition != 0:
            self.currentPosition -= 1
            self.create_path(self.changing_points[self.currentPosition])
            if len(self.path_to_follow) > 0:
                self.path_to_follow.remove(self.path_to_follow[0])
                self.move(self.futurePoint(self.direction))
                self.number_of_steps += 1
                self.simulation.detector_number_of_steps += 1

        elif len(self.path_to_follow) > 0:
            self.direction = self.path_to_follow[0]
            if self.canMove(self.futurePoint(self.direction)):
                self.path_to_follow.remove(self.path_to_follow[0])
                self.move(self.futurePoint(self.direction))
                self.number_of_steps += 1
                self.simulation.detector_number_of_steps += 1
            else:
                self.create_path(self.changing_points[self.currentPosition])
                if len(self.path_to_follow) > 0:
                    self.path_to_follow.remove(self.path_to_follow[0])
                    self.move(self.futurePoint(self.direction))
                    self.number_of_steps += 1
                    self.simulation.detector_number_of_steps += 1

        elif self.currentPosition == len(self.changing_points) - 1 or self.currentPosition == 0:
            self.reversing = not self.reversing
            self.path_to_follow = []

    def create_path(self, point):

        self.path_to_follow = []
        points = self.point.a_Star_search(point, self.simulation)
        self.actions(points)
        self.pontos = points
        if len(self.path_to_follow) > 0:
            self.direction = self.path_to_follow[0]

    def actions(self, points):
        for i in range(len(points) - 1):
            x_move = points[i].x - points[i + 1].x
            if x_move == 1:
                self.path_to_follow.append(Direction.West)
            elif x_move == -1:
                self.path_to_follow.append(Direction.East)

            y_move = points[i].y - points[i + 1].y
            if y_move == 1:
                self.path_to_follow.append(Direction.North)
            elif y_move == -1:
                self.path_to_follow.append(Direction.South)

    def current_fov(self):
        fov = []

        for y in range(self.point.y - 2, self.point.y + 3):
            for j in range(self.point.x - 2, self.point.x + 3):
                if (0 <= y <= 31) and (0 <= j <= 59):
                    fov.append(Position(j, y))
        return fov


class RobotComplexReactiveCollector(Robot):

    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y, "c.png")
        self.path_to_follow = []
        self.desires = {}
        self.myTrash = None
        self.distance_to_myTrash = None
        self.currentTrash = None
        self.closest_container = None
        self.distance_to_closest_container = sys.maxsize
        self.desire = None
        self.updatedMyTrash = False
        self.updatedClosestContainer = False
        self.direction = None
        self.pontos = []
        self.fovPoints = []
        self.calculate_containerFovPoints()

        self.number_of_steps = 0
        self.collected_trash = 0
        self.delivered_trash = 0

    def decision(self) -> None:

        self.assignTrash()

        for point in self.fov:
            if self.simulation.tile_dict[point].has_trash and point not in self.simulation.trash_to_be_assigned:
                distance = distance_between_points(self.point, point)
                can_I_assign_It = self.verify_Others_Trash(point)
                if self.myTrash is not None and self.myTrash.point == point:
                    continue

                elif self.myTrash is None and can_I_assign_It:

                    self.updateMyTrash(self.simulation.trash_dict[point], distance)

                elif distance < self.distance_to_myTrash and can_I_assign_It:

                    self.simulation.trash_to_be_assigned[self.myTrash.point] = self.myTrash
                    self.updateMyTrash(self.simulation.trash_dict[point], distance)

                else:
                    self.simulation.trash_to_be_assigned[point] = self.simulation.trash_dict[point]

        self.updateClosestContainer()

        if self.myTrash is not None:
            self.distance_to_myTrash = distance_between_points(self.point, self.myTrash.point)

        self.calculateDesire()
        for tile in self.simulation.container_FOV_Tiles:
            if self.point == tile.point and self.has_in_storage > 0:
                self.deliverToContainer()

        if self.desire == "deliver" and self.point == self.closest_container.point:
            self.deliverToContainer()

        elif self.desire == "deliver" and (
                len(self.path_to_follow) == 0 or self.updatedClosestContainer) and self.canMove(
            self.closest_container.point):
            self.create_path(self.closest_container.point)
            if self.canMove(self.futurePoint(self.direction)):
                self.path_to_follow.remove(self.path_to_follow[0])
                self.move(self.futurePoint(self.direction))
                self.number_of_steps += 1
                self.simulation.collector_number_of_steps += 1

        elif self.desire == "deliver" and len(self.path_to_follow) > 0:
            self.direction = self.path_to_follow[0]
            if not self.canMove(self.futurePoint(self.direction)):
                for ponto in self.pontos:
                    self.removeHighlight(ponto)
                self.path_to_follow = []

            else:
                self.path_to_follow.remove(self.path_to_follow[0])
                self.move(self.futurePoint(self.direction))
                self.number_of_steps += 1
                self.simulation.collector_number_of_steps += 1

        elif self.desire == "pickup" and self.point == self.myTrash.point:
            self.pickUpTrash()

        elif self.desire == "pickup" and (
                len(self.path_to_follow) == 0 or self.updatedClosestContainer) and self.canMove(self.myTrash.point):
            self.create_path(self.myTrash.point)
            if self.canMove(self.futurePoint(self.direction)):
                self.path_to_follow.remove(self.path_to_follow[0])
                self.move(self.futurePoint(self.direction))
                self.number_of_steps += 1
                self.simulation.collector_number_of_steps += 1

        elif self.desire == "pickup" and len(self.path_to_follow) > 0:
            self.direction = self.path_to_follow[0]
            if not self.canMove(self.futurePoint(self.direction)):
                for ponto in self.pontos:
                    self.removeHighlight(ponto)
                self.path_to_follow = []

            else:
                self.path_to_follow.remove(self.path_to_follow[0])
                self.move(self.futurePoint(self.direction))
                self.number_of_steps += 1
                self.simulation.collector_number_of_steps += 1

        elif self.desire == "random":
            for ponto in self.pontos:
                self.removeHighlight(ponto)
            self.direction = random_direction()
            while not self.canMove(self.futurePoint(self.direction)):
                self.direction = random_direction()
            self.move(self.futurePoint(self.direction))
            self.number_of_steps += 1
            self.simulation.collector_number_of_steps += 1

        self.updatedClosestContainer = False
        self.updatedMyTrash = False

    def ClosestTrash(self):
        closest_trash = None
        my_distance = sys.maxsize
        for trash in self.simulation.trash_to_be_assigned.values():
            distance_to_trash = distance_between_points(self.point, trash.point)
            if distance_to_trash < my_distance:
                my_distance = distance_to_trash
                closest_trash = trash
        return closest_trash, my_distance

    def am_I_the_Closest_Robot(self, closestPoint, correspondingDistance) -> bool:
        for robot in self.simulation.robot_collectors:
            distance_to_trash = distance_between_points(robot.point, closestPoint)
            if distance_to_trash < correspondingDistance:
                return False
        return True

    def pickUpTrash(self):
        self.simulation.tile_dict[self.point].has_trash = False
        if self.point in self.simulation.trash_dict:
            trash = self.simulation.trash_dict[self.point]
            self.simulation.trash_group.remove(trash)
            self.simulation.trash_dict.pop(self.point)
            self.has_in_storage += 1

        self.myTrash = None
        self.path_to_follow = []
        self.desire = "random"
        self.collected_trash += 1
        self.simulation.trash_collected += 1

    def deliverToContainer(self):
        self.delivered_trash += self.has_in_storage
        self.simulation.trash_delivered += self.has_in_storage
        self.has_in_storage = 0
        self.path_to_follow = []
        self.desire = "random"

    def actions(self, points):
        for i in range(len(points) - 1):
            x_move = points[i].x - points[i + 1].x
            if x_move == 1:
                self.path_to_follow.append(Direction.West)
            elif x_move == -1:
                self.path_to_follow.append(Direction.East)

            y_move = points[i].y - points[i + 1].y
            if y_move == 1:
                self.path_to_follow.append(Direction.North)
            elif y_move == -1:
                self.path_to_follow.append(Direction.South)

    def current_fov(self):
        fov = []

        for y in range(self.point.y - 1, self.point.y + 2):
            for j in range(self.point.x - 1, self.point.x + 2):
                if (0 <= y <= 31) and (0 <= j <= 59):
                    fov.append(Position(j, y))
        return fov

    def updateClosestContainer(self):
        distance_min = sys.maxsize
        for container in self.simulation.container_FOV_Tiles:
            distance = distance_between_points(self.point, container.point)
            if distance < distance_min:
                distance_min = distance
                self.distance_to_closest_container = distance
                self.closest_container = container
                self.updatedClosestContainer = True

    def updateMyTrash(self, closest_trash, my_distance):
        self.myTrash = closest_trash
        self.distance_to_myTrash = my_distance
        self.updatedMyTrash = True

    def calculateDesire(self):
        if self.has_in_storage == self.max_storage:
            self.setDesire("deliver")

        elif self.has_in_storage > 0 and self.myTrash is None:
            self.setDesire("deliver")

        elif self.has_in_storage >= 2 and self.distance_to_myTrash > self.distance_to_closest_container:
            self.setDesire("deliver")

        elif len(self.simulation.trash_dict) == 0 and self.has_in_storage > 0:
            self.setDesire("deliver")

        elif self.myTrash is not None:
            self.setDesire("pickup")

        else:
            self.desire = "random"

    def setDesire(self, desire):
        if self.desire != desire:
            self.path_to_follow = []
        self.desire = desire

    def create_path(self, point):

        for ponto in self.pontos:
            self.removeHighlight(ponto)

        self.path_to_follow = []
        points = self.point.a_Star_search(point, self.simulation)
        self.actions(points)
        self.pontos = points
        self.direction = self.path_to_follow[0]

        for point in points[1:]:
            orange = Highlight(self.simulation, point.x, point.y)
            self.simulation.tile_group.add(orange)

    def calculate_containerFovPoints(self):
        for tile in self.simulation.container_FOV_Tiles:
            self.fovPoints.append(tile.point)

    def removeHighlight(self, point):
        if point in self.fovPoints:
            container = ContainerFieldOfView(self.simulation, point.x, point.y)
            self.simulation.tile_group.add(container)
        else:
            tile = Park(self.simulation, point.x, point.y)
            self.simulation.tile_group.add(tile)

    def assignTrash(self):
        if len(self.simulation.trash_to_be_assigned) > 0:

            closest_trash_pair = self.ClosestTrash()
            closest_trash = closest_trash_pair[0]
            my_distance = closest_trash_pair[1]

            am_I_The_Closest = self.am_I_the_Closest_Robot(closest_trash.point, my_distance)
            if am_I_The_Closest and self.myTrash is None:
                self.simulation.trash_to_be_assigned.pop(closest_trash.point)
                self.updateMyTrash(closest_trash, my_distance)

            elif am_I_The_Closest and self.distance_to_myTrash > my_distance:
                self.simulation.trash_to_be_assigned[self.myTrash.point] = self.myTrash
                self.simulation.trash_to_be_assigned.pop(closest_trash.point)
                self.updateMyTrash(closest_trash, my_distance)

    def verify_Others_Trash(self, point):
        for robot in self.simulation.robot_collectors:
            if robot.myTrash is not None:
                if robot.point != self.point and robot.myTrash.point == point:
                    return False
        return True


class RobotComplexReactiveDetector(Robot):
    def __init__(self, simulation, x, y):
        super().__init__(simulation, x, y, "de.png")
        self.currentPosition = 0
        self.direction = None
        self.reversing = False
        self.sweep_target = None
        self.path_to_follow = []
        self.sector = None
        self.number_of_detected_trash_in_sector = 0
        self.sweeping = False
        self.previously_sweeped = None
        self.closest_corner = None
        self.number_of_steps = 0
        self.detected_trash = 0
        self.current_sectors_local = []
        self.flag = False
        self.upwards = False
        self.sector_i_am_in = None

    def decision(self) -> None:

        for sector in self.simulation.sectors:
            if self.point in sector.sector_tiles:
                self.sector_i_am_in = sector

        if not self.sweeping:

            for point in self.fov:
                if self.simulation.tile_dict[point].has_trash and point not in self.simulation.detected_trash:
                    self.simulation.detected_trash[point] = self.simulation.trash_dict[point]
                    self.simulation.trash_to_be_assigned[point] = self.simulation.trash_dict[point]
                    self.detected_trash += 1
                    self.simulation.total_detected_trash += 1

            if self.sector is None:

                random_prob = random.randint(1, 100)
                if random_prob <= self.simulation.randomized_factor_percentage * 100:
                    self.sector = random.choice(self.simulation.sectors)
                    while self.sector.isChosen or self.sector in self.simulation.previously_sweeped_sectors:
                        self.sector = random.choice(self.simulation.sectors)

                else:
                    max_trash_belief = 0
                    for sector in self.simulation.sectors:
                        if sector.trash_belief > max_trash_belief and not sector.isChosen and sector not in self.simulation.previously_sweeped_sectors:
                            max_trash_belief = sector.trash_belief
                            self.sector = sector

                closest_corner_distance = sys.maxsize
                for corner in self.sector.corners:
                    if distance_between_points(self.point, corner) < closest_corner_distance:
                        closest_corner_distance = distance_between_points(self.point, corner)
                        self.closest_corner = corner

                self.updatePath()

                self.create_path(self.closest_corner)
                self.sector.isChosen = True
                self.simulation.current_chosen_sectors.append(self.sector)
                self.updateLocalSector()

            elif self.flag:

                if len(self.path_to_follow) == 0:
                    if self.upwards:
                        self.closest_corner = Position(self.point.x, self.point.y - 5)
                        self.create_path(self.closest_corner)
                    else:
                        self.closest_corner = Position(self.point.x, self.point.y + 5)
                        self.create_path(self.closest_corner)
                    self.flag = False

                elif len(self.path_to_follow) > 0:
                    self.direction = self.path_to_follow[0]
                    if self.canMove(self.futurePoint(self.direction)):
                        self.path_to_follow.remove(self.path_to_follow[0])
                        self.move(self.futurePoint(self.direction))
                        self.number_of_steps += 1
                    else:
                        self.create_path(self.closest_corner)
                        if len(self.path_to_follow) > 0:
                            self.path_to_follow.remove(self.path_to_follow[0])
                            self.move(self.futurePoint(self.direction))
                            self.number_of_steps += 1

            elif len(self.path_to_follow) == 0:
                self.sweeping = True
                self.defineMySweep()

            elif len(self.path_to_follow) > 0:
                if self.current_sectors_local == self.simulation.current_chosen_sectors:
                    self.direction = self.path_to_follow[0]
                    if self.canMove(self.futurePoint(self.direction)):
                        self.path_to_follow.remove(self.path_to_follow[0])
                        self.move(self.futurePoint(self.direction))
                        self.number_of_steps += 1
                    else:
                        self.create_path(self.closest_corner)
                        if len(self.path_to_follow) > 0:
                            self.path_to_follow.remove(self.path_to_follow[0])
                            self.move(self.futurePoint(self.direction))
                            self.number_of_steps += 1
                else:

                    self.updateLocalSector()
                    self.updatePath()
                    self.create_path(self.closest_corner)
                    if len(self.path_to_follow) > 0:
                        self.path_to_follow.remove(self.path_to_follow[0])
                        self.move(self.futurePoint(self.direction))
                        self.number_of_steps += 1

        elif self.sweeping:

            for point in self.fov:
                if self.simulation.tile_dict[point].has_trash and point not in self.simulation.detected_trash:
                    self.simulation.detected_trash[point] = self.simulation.trash_dict[point]
                    self.simulation.trash_to_be_assigned[point] = self.simulation.trash_dict[point]
                    self.detected_trash += 1
                    self.simulation.total_detected_trash += 1
                    self.sector.trash_belief += 1

            if len(self.path_to_follow) == 0 and not self.reversing and self.currentPosition != len(
                    self.sweep_target) - 1:
                self.currentPosition += 1
                self.create_path(self.sweep_target[self.currentPosition])
                if len(self.path_to_follow) > 0:
                    self.path_to_follow.remove(self.path_to_follow[0])
                    self.move(self.futurePoint(self.direction))
                    self.number_of_steps += 1
                    self.simulation.detector_number_of_steps += 1

            elif len(self.path_to_follow) == 0 and self.reversing and self.currentPosition != 0:
                self.currentPosition -= 1
                self.create_path(self.sweep_target[self.currentPosition])
                if len(self.path_to_follow) > 0:
                    self.path_to_follow.remove(self.path_to_follow[0])
                    self.move(self.futurePoint(self.direction))
                    self.number_of_steps += 1
                    self.simulation.detector_number_of_steps += 1

            elif (len(self.path_to_follow) == 0 and self.currentPosition == 0 and self.reversing) or (
                    len(self.path_to_follow) == 0 and self.currentPosition == len(
                self.sweep_target) - 1 and not self.reversing):

                self.sector.times_visited += 1
                self.sector.trash_belief = self.sector.trash_belief / self.sector.times_visited
                if self.previously_sweeped is not None:
                    self.simulation.previously_sweeped_sectors.remove(self.previously_sweeped)
                self.sector.isChosen = False
                self.simulation.current_chosen_sectors.remove(self.sector)
                self.updateLocalSector()
                self.previously_sweeped = self.sector
                self.sector = None
                self.simulation.previously_sweeped_sectors.append(self.previously_sweeped)
                if self.simulation.randomized_factor_percentage > 0.05:
                    self.simulation.randomized_factor_percentage -= 0.3
                elif self.simulation.randomized_factor_percentage < 0.05:
                    self.simulation.randomized_factor_percentage = 0.05
                self.sweeping = False

            elif len(self.path_to_follow) > 0:
                self.direction = self.path_to_follow[0]
                if self.canMove(self.futurePoint(self.direction)):
                    self.path_to_follow.remove(self.path_to_follow[0])
                    self.move(self.futurePoint(self.direction))
                    self.number_of_steps += 1
                    self.simulation.detector_number_of_steps += 1
                else:
                    self.create_path(self.sweep_target[self.currentPosition])
                    if len(self.path_to_follow) > 0:
                        self.path_to_follow.remove(self.path_to_follow[0])
                        self.move(self.futurePoint(self.direction))
                        self.number_of_steps += 1
                        self.simulation.detector_number_of_steps += 1

    def updateLocalSector(self):
        self.current_sectors_local = []
        for sector in self.simulation.current_chosen_sectors:
            self.current_sectors_local.append(sector)

    def updatePath(self):

        if self.sector_i_am_in.sector_number == 1 and self.sector.sector_number == 3 and self.simulation.sectors[1] in self.simulation.current_chosen_sectors:
            self.closest_corner = self.simulation.sectors[5].corners[0]
            self.flag = True
            self.upwards = True

        elif self.sector_i_am_in.sector_number == 3 and self.sector.sector_number == 1 and self.simulation.sectors[1] in self.simulation.current_chosen_sectors:
            self.closest_corner = self.simulation.sectors[3].corners[1]
            self.flag = True
            self.upwards = True

        elif self.sector_i_am_in.sector_number == 4 and self.sector.sector_number == 6 and self.simulation.sectors[4] in self.simulation.current_chosen_sectors:
            self.closest_corner = self.simulation.sectors[2].corners[2]
            self.flag = True
            self.upwards = False

        elif self.sector_i_am_in.sector_number == 6 and self.sector.sector_number == 4 and self.simulation.sectors[4] in self.simulation.current_chosen_sectors:
            self.closest_corner = self.simulation.sectors[0].corners[3]
            self.flag = True
            self.upwards = False

    def create_path(self, point):

        self.path_to_follow = []
        points = self.point.a_Star_search(point, self.simulation)
        self.actions(points)
        self.pontos = points
        if len(self.path_to_follow) > 0:
            self.direction = self.path_to_follow[0]

    def actions(self, points):
        for i in range(len(points) - 1):
            x_move = points[i].x - points[i + 1].x
            if x_move == 1:
                self.path_to_follow.append(Direction.West)
            elif x_move == -1:
                self.path_to_follow.append(Direction.East)

            y_move = points[i].y - points[i + 1].y
            if y_move == 1:
                self.path_to_follow.append(Direction.North)
            elif y_move == -1:
                self.path_to_follow.append(Direction.South)

    def current_fov(self):
        fov = []

        for y in range(self.point.y - 2, self.point.y + 3):
            for j in range(self.point.x - 2, self.point.x + 3):
                if (0 <= y <= 31) and (0 <= j <= 59):
                    fov.append(Position(j, y))
        return fov

    def defineMySweep(self):
        if self.closest_corner == self.sector.corners[0]:
            self.sweep_target = self.sector.sweep_points
            self.reversing = False
            self.currentPosition = 0

        if self.closest_corner == self.sector.corners[1]:
            self.sweep_target = self.sector.sweep_points
            self.reversing = True
            self.currentPosition = len(self.sweep_target) - 1

        if self.closest_corner == self.sector.corners[2]:
            self.sweep_target = self.sector.alternative_sweep_points
            self.reversing = False
            self.currentPosition = 0

        if self.closest_corner == self.sector.corners[3]:
            self.sweep_target = self.sector.alternative_sweep_points
            self.reversing = True
            self.currentPosition = len(self.sweep_target) - 1
