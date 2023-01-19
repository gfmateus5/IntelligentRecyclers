import time
from typing import List

from button import Button
from robot import *
from sector import *
import random


class Simulation:
    def __init__(self):
        pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode((PYGAME_WIDTH, PYGAME_HEIGHT))
        self.title = pygame.font.SysFont("Impact", 50).render("Intelligent Recyclers", True, "#FFFFFF")
        self.title_rect = self.title.get_rect(center=(PYGAME_WIDTH / 2, 76))

        self.tile_group = pygame.sprite.Group()
        self.robot_group = pygame.sprite.Group()
        self.trash_group = pygame.sprite.Group()

        self.robot_list = []
        self.robot_detectors = []
        self.robot_collectors = []

        self.container_FOV = []
        self.container_FOV_Tiles = []

        self.tile_dict = {}
        self.container_list: List[Tile] = []

        self.detected_trash = {}
        self.trash_to_be_assigned = {}
        self.trash_dict = {}

        self.sector_trash_spawn_probabilities = [0.3, 0.25, 0.2, 0.1, 0.1, 0.05]
        self.sectors = []
        self.sector1 = None
        self.sector2 = None
        self.sector3 = None
        self.sector4 = None
        self.sector5 = None
        self.sector6 = None

        self.timer = 0

        self.random_collectors_button = None
        self.random_collectors_initiate = False

        self.reactive_collectors_button = None
        self.reactive_collectors_initiate = False

        self.intelligent_collectors_button = None
        self.intelligent_collectors_initiate = False

        self.final_prototype_button = None
        self.final_prototype_initiate = False

        self.mode_chosen = False
        self.simulation_started = False
        self.randomized_factor_percentage = 1

        self.previously_sweeped_sectors = []
        self.current_chosen_sectors = []

        # Analytics

        self.start_ticks = pygame.time.get_ticks()
        self.current_time = 0

        self.total_trash_spawned = 0
        self.total_detected_trash = 0

        self.total_number_of_steps = 0
        self.detector_number_of_steps = 0
        self.collector_number_of_steps = 0

        self.trash_collected = 0
        self.trash_delivered = 0

    def create_tiles(self):
        container1 = [(9, 6), (10, 6), (9, 7), (10, 7)]
        container2 = [(29, 6), (30, 6), (29, 7), (30, 7)]
        container3 = [(49, 6), (50, 6), (49, 7), (50, 7)]
        container4 = [(9, 24), (10, 24), (9, 25), (10, 25)]
        container5 = [(29, 24), (30, 24), (29, 25), (30, 25)]
        container6 = [(49, 24), (50, 24), (49, 25), (50, 25)]

        containers = [container1, container2, container3, container4, container5, container6]
        self.container_FOV = self.obtainFieldOfView(containers)

        for y in range(0, 32, 1):
            for x in range(0, 60, 1):
                if (x, y) in container1 or (x, y) in container2 or (x, y) in container3 or (x, y) in container4 or (
                        x, y) in container5 or (x, y) in container6:
                    tile = Container(self, x, y)
                    self.container_list.append(tile)

                elif (x, y) in self.container_FOV:
                    tile = ContainerFieldOfView(self, x, y)
                    self.container_FOV_Tiles.append(tile)

                else:
                    tile = Park(self, x, y)

                self.tile_group.add(tile)
                self.tile_dict[tile.point] = tile

    def obtainFieldOfView(self, containers):
        # Se tu leste esta função, peço desculpa
        fov = []
        for container in containers:
            posZero = container[0]
            posOne = container[1]
            posTwo = container[2]
            posThree = container[3]

            fov.append((posZero[0] - 1, posZero[1]))
            fov.append((posZero[0] - 1, posZero[1] - 1))
            fov.append((posZero[0], posZero[1] - 1))
            fov.append((posOne[0], posOne[1] - 1))
            fov.append((posOne[0] + 1, posOne[1] - 1))
            fov.append((posOne[0] + 1, posOne[1]))
            fov.append((posTwo[0] - 1, posTwo[1]))
            fov.append((posTwo[0] - 1, posTwo[1] + 1))
            fov.append((posTwo[0], posTwo[1] + 1))
            fov.append((posThree[0], posThree[1] + 1))
            fov.append((posThree[0] + 1, posThree[1] + 1))
            fov.append((posThree[0] + 1, posThree[1]))
        return fov

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.display.quit()
                pygame.quit()
                sys.exit()

        if not self.mode_chosen and self.random_collectors_button.check_click():
            self.random_collectors_initiate = True
            self.mode_chosen = True
            print("random collectors")

        elif not self.mode_chosen and self.reactive_collectors_button.check_click():
            self.reactive_collectors_initiate = True
            self.mode_chosen = True
            print("reactive collectors")

        elif not self.mode_chosen and self.intelligent_collectors_button.check_click():
            self.intelligent_collectors_initiate = True
            self.mode_chosen = True
            print("intelligent collectors")

        elif not self.mode_chosen and self.final_prototype_button.check_click():
            self.final_prototype_initiate = True
            self.mode_chosen = True
            print("intelligent collectors")

    def draw(self):
        self.tile_group.draw(self.screen)
        self.trash_group.draw(self.screen)
        self.robot_group.draw(self.screen)

        self.uiStatistics()
        if self.final_prototype_initiate:
            self.grid()

        pygame.display.flip()

    def create_random_collectors(self):
        robot = RandomCollector(self, 16, 16)
        self.robot_group.add(robot)
        self.robot_list.append(robot)
        self.robot_collectors.append(robot)
        robot = RandomCollector(self, 17, 16)
        self.robot_group.add(robot)
        self.robot_list.append(robot)
        self.robot_collectors.append(robot)
        robot = RandomCollector(self, 18, 16)
        self.robot_group.add(robot)
        self.robot_list.append(robot)
        self.robot_collectors.append(robot)

    def create_reactive_collectors(self):
        posx = 32
        for i in range(3):
            robot = RobotSimpleReactiveCollector(self, posx, 16)
            self.robot_group.add(robot)
            self.robot_list.append(robot)
            self.robot_collectors.append(robot)
            posx += 1

    def create_reactive_detector_robots(self):
        x_value = 2
        for i in range(2):
            robot = RobotSimpleReactiveDetector(self, x_value, 2)
            self.robot_group.add(robot)
            self.robot_list.append(robot)
            self.robot_detectors.append(robot)
            x_value += 30

    def create_reactive_complex_detector_robots(self):
        x_value = 2
        for i in range(2):
            robot = RobotComplexReactiveDetector(self, x_value, 2)
            self.robot_group.add(robot)
            self.robot_list.append(robot)
            self.robot_detectors.append(robot)
            x_value += 20

    def create_reactive_complex_robots(self):
        for i in range(3):
            robot_possible_pos = self.possibleReactiveRobotPositions()
            point = random.choice(robot_possible_pos).point
            robot = RobotComplexReactiveCollector(self, point.x, point.y)
            self.robot_group.add(robot)
            self.robot_list.append(robot)
            self.robot_collectors.append(robot)

    def possibleReactiveRobotPositions(self):
        park_list = list(self.tile_dict.values())
        for x in self.tile_dict.values():
            if x.__class__ == Park and not x.has_trash and x.point.x in range(1, 60) and x.point.y in range(1, 31):
                for robot in self.robot_list:
                    if x.point == robot.point:
                        park_list.remove(x)
            else:
                park_list.remove(x)

        return park_list

    def init_environment(self):
        if self.random_collectors_initiate:
            self.create_random_collectors()
        elif self.reactive_collectors_initiate:
            self.create_reactive_collectors()
        elif self.intelligent_collectors_initiate:
            self.create_reactive_detector_robots()
            self.create_reactive_complex_robots()
        elif self.final_prototype_initiate:
            self.create_reactive_complex_detector_robots()
            self.create_reactive_complex_robots()

    def initial_draw(self):
        self.screen.blit(self.title, self.title_rect)

        analytics_border = pygame.Rect((32, 768), (960, 150))
        pygame.draw.rect(self.screen, "#FFFFFF", analytics_border)

        statistics_box1 = pygame.Rect((36, 772), (314, 142))
        pygame.draw.rect(self.screen, "#000000", statistics_box1)
        statistics_box2 = pygame.Rect((354, 772), (316, 142))
        pygame.draw.rect(self.screen, "#000000", statistics_box2)
        statistics_box3 = pygame.Rect((674, 772), (314, 142))
        pygame.draw.rect(self.screen, "#000000", statistics_box3)

        a = pygame.font.SysFont("Calibri", 20).render("General Statistics", True, "#FFFFFF")
        b = a.get_rect(center=(192, 795))
        self.screen.blit(a, b)
        a = pygame.font.SysFont("Calibri", 15).render("Total Trash Spawned:", True, "#FFFFFF")
        b = a.get_rect(topleft=(50, 820))
        self.screen.blit(a, b)
        a = pygame.font.SysFont("Calibri", 15).render("Total Number of Steps:", True, "#FFFFFF")
        b = a.get_rect(topleft=(50, 845))
        self.screen.blit(a, b)

        a = pygame.font.SysFont("Calibri", 20).render("Detector Statistics", True, "#FFFFFF")
        b = a.get_rect(center=(512, 795))
        self.screen.blit(a, b)
        a = pygame.font.SysFont("Calibri", 15).render("Trash Detected:", True, "#FFFFFF")
        b = a.get_rect(topleft=(370, 820))
        self.screen.blit(a, b)
        a = pygame.font.SysFont("Calibri", 15).render("Number of Steps:", True, "#FFFFFF")
        b = a.get_rect(topleft=(370, 845))
        self.screen.blit(a, b)

        a = pygame.font.SysFont("Calibri", 20).render("Collector Statistics", True, "#FFFFFF")
        b = a.get_rect(center=(832, 795))
        self.screen.blit(a, b)
        a = pygame.font.SysFont("Calibri", 15).render("Trash Collected:", True, "#FFFFFF")
        b = a.get_rect(topleft=(690, 820))
        self.screen.blit(a, b)
        a = pygame.font.SysFont("Calibri", 15).render("Trash Delivered:", True, "#FFFFFF")
        b = a.get_rect(topleft=(690, 845))
        self.screen.blit(a, b)
        a = pygame.font.SysFont("Calibri", 15).render("Number of Steps:", True, "#FFFFFF")
        b = a.get_rect(topleft=(690, 870))
        self.screen.blit(a, b)

        self.uiStatistics()

        self.tile_group.draw(self.screen)

        self.draw_buttons()

        self.trash_group.draw(self.screen)

        self.grid()
        pygame.display.flip()

    def simulation_loop(self):

        self.initial_draw()

        while not self.mode_chosen:
            self.check_events()
            self.draw_buttons()

        self.init_environment()
        self.simulation_started = True

        self.start_ticks = pygame.time.get_ticks()

        while self.simulation_started:

            self.timer += 1
            if self.timer > 0 and self.timer % 15 == 0:
                self.spawnTrash()

            self.check_events()

            for agent in self.robot_detectors:
                agent.decision()

            for agent in self.robot_collectors:
                agent.decision()

            self.total_number_of_steps = self.detector_number_of_steps + self.collector_number_of_steps

            self.current_time = 60 - int((pygame.time.get_ticks() - self.start_ticks) / 1000)

            self.draw()

            if self.current_time <= 0:
                self.simulation_started = False

            time.sleep(0.1)

        a = pygame.font.SysFont("Impact", 50).render(" Simulation Ended ", True, (255, 255, 255), (0, 0, 0))
        b = a.get_rect(center=(PYGAME_WIDTH / 2, 480))
        self.screen.blit(a, b)
        pygame.display.flip()

        while True:
            self.check_events()

    def initiate(self):
        self.create_tiles()
        self.initiateButtons()
        self.initiateSectors()

    def initiateButtons(self):
        self.random_collectors_button = Button('Random Collectors', 216, 40, (140, 172), self.screen)
        self.reactive_collectors_button = Button('Reactive Collectors', 216, 40, (388, 172), self.screen)
        self.intelligent_collectors_button = Button('Intelligent Collectors', 216, 40, (636, 172), self.screen)
        self.final_prototype_button = Button('Sector Prototype', 216, 40, (884, 172), self.screen)

    def isWalkable(self, neighbour, start, mySector, endSector):
        neighbourPoint = Position(neighbour.x, neighbour.y)
        if self.tile_dict[neighbourPoint].__class__ != Container:
            robot_doing_astar = None
            for robot in self.robot_list:
                if robot.point.x == start.x and robot.point.y == start.y:
                    robot_doing_astar = robot
            if self.final_prototype_initiate and robot_doing_astar.__class__ == RobotComplexReactiveDetector:
                for sector in self.sectors:
                    if sector != mySector and sector != endSector and sector.isChosen and self.checkIfInSector(
                            neighbourPoint, sector):
                        return "Container"

            for robot in self.robot_list:
                if robot.point.x == neighbour.x and robot.point.y == neighbour.y and abs(robot.point.x - start.x) + abs(
                        robot.point.y - start.y) == 1:
                    return "Detector"
            return "Doable"
        return "Container"

    def draw_buttons(self):
        self.random_collectors_button.draw()
        self.reactive_collectors_button.draw()
        self.intelligent_collectors_button.draw()
        self.final_prototype_button.draw()

    def initiateSectors(self):

        self.sector1 = Sector((0, 0), self, 1)
        self.sectors.append(self.sector1)

        self.sector2 = Sector((20, 0), self, 2)
        self.sectors.append(self.sector2)

        self.sector3 = Sector((40, 0), self, 3)
        self.sectors.append(self.sector3)

        self.sector4 = Sector((0, 16), self, 4)
        self.sectors.append(self.sector4)

        self.sector5 = Sector((20, 16), self, 5)
        self.sectors.append(self.sector5)

        self.sector6 = Sector((40, 16), self, 6)
        self.sectors.append(self.sector6)

        trash_to_be_spawned = random.randint(50, 80)
        i = 1
        prev_prob = 1

        for sector in self.sectors:
            prob = random.choice(self.sector_trash_spawn_probabilities)
            sector.range_for_spawn = [prev_prob, int(prev_prob + prob * 100 - 1)]
            prev_prob = int(prev_prob + prob * 100)

            self.sector_trash_spawn_probabilities.remove(prob)

            sector.probability = prob

            trash_in_sector = int(trash_to_be_spawned * sector.probability)
            sector.spawnTrash(trash_in_sector)

            i += 1

    def spawnTrash(self):
        i = 1
        for sector in self.sectors:
            for j in range(8):
                randomly = random.randint(1, 100)
                if sector.range_for_spawn[0] <= randomly <= sector.range_for_spawn[1]:
                    sector.spawnTrash(1)
                    break
            i += 1

    def grid(self):
        pygame.draw.line(self.screen, WHITE, (32, Y_MARGIN - 8 + 256), (991, Y_MARGIN - 8 + 256))
        pygame.draw.line(self.screen, WHITE, (32 + 320, Y_MARGIN - 8), (32 + 320, Y_MARGIN - 8 + 511))
        pygame.draw.line(self.screen, WHITE, (32 + 320 + 320, Y_MARGIN - 8), (32 + 320 + 320, Y_MARGIN - 8 + 511))

    def uiStatistics(self):
        a = pygame.font.SysFont("Calibri", 15).render(str(self.total_trash_spawned), True, (255, 255, 255), (0, 0, 0))
        self.screen.blit(a, (180, 820))

        a = pygame.font.SysFont("Calibri", 15).render(str(self.total_number_of_steps), True, (255, 255, 255), (0, 0, 0))
        self.screen.blit(a, (190, 845))

        a = pygame.font.SysFont("Calibri", 15).render(str(self.total_detected_trash), True, (255, 255, 255), (0, 0, 0))
        self.screen.blit(a, (470, 820))

        a = pygame.font.SysFont("Calibri", 15).render(str(self.detector_number_of_steps), True, (255, 255, 255),
                                                      (0, 0, 0))
        self.screen.blit(a, (480, 845))

        a = pygame.font.SysFont("Calibri", 15).render(str(self.trash_collected), True, (255, 255, 255), (0, 0, 0))
        self.screen.blit(a, (790, 820))

        a = pygame.font.SysFont("Calibri", 15).render(str(self.trash_delivered), True, (255, 255, 255), (0, 0, 0))
        self.screen.blit(a, (790, 845))

        a = pygame.font.SysFont("Calibri", 15).render(str(self.collector_number_of_steps), True, (255, 255, 255),
                                                      (0, 0, 0))
        self.screen.blit(a, (800, 870))

        if self.simulation_started:
            a = pygame.font.SysFont("Impact", 50).render(str(self.current_time) + '     ', True, (255, 255, 255),
                                                         (0, 0, 0))
            self.screen.blit(a, (860, 45))

    def checkIfInSector(self, neighbourPoint, sector):
        topCorner = sector.corners[0]
        lowerCorner = sector.corners[3]
        if topCorner.x - 2 <= neighbourPoint.x <= lowerCorner.x + 2 and topCorner.y - 2 <= neighbourPoint.y <= lowerCorner.y + 2:
            return True
        return False
