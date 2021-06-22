import pygame
from math import pow
from copy import deepcopy
from time import sleep

pygame.init()

class Grid:
    # Function to initialize different, though limited, sizes of the grid
    def __init__(self):
        self.grid: list = [
            [0 for _ in range(128)] for _ in range(64)
        ]
        self.future: list = deepcopy(self.grid)
        self.zoom_levels: list = [
            [(0, 63), (16, 47), (24, 39), (28, 35), (30, 33)],
            [(0, 127), (32, 95), (48, 79), (56, 71), (60, 67)]
        ]
        self.zoom_level: int = 1

    def get_visible_grid_portion(self) -> list:
        return [
            row[
                self.zoom_levels[1][self.zoom_level][0]
                : self.zoom_levels[1][self.zoom_level][1] + 1
            ]
            for row in self.grid[
                self.zoom_levels[1][self.zoom_level][0]
                : self.zoom_levels[1][self.zoom_level][1] + 1
            ]
        ]

    def grid_is_alive(self) -> bool:
        for row in self.grid:
            if 1 in row:
                return True
        return False

    def get_surrounding_alive_cells(self, x: int, y: int) -> int:
        surrounding_alive_cells: int = 0
        for xc in range(x - 1, x + 2):
            for yc in range(y - 1, y + 2):
                if xc in [-1, 64] or yc in [-1, 128] or [xc, yc] == [x, y]:
                    continue
                if self.grid[xc][yc]:
                    surrounding_alive_cells += 1
        return surrounding_alive_cells

    def update_cell_survival(self, x: int, y: int) -> None:
        surrounding_alive_cells = self.get_surrounding_alive_cells(x, y)
        if not self.grid[x][y]:
            if surrounding_alive_cells == 3:
                self.future[x][y] = 1
        if self.grid[x][y]:
            if surrounding_alive_cells in [2, 3]:
                self.future[x][y] = 1
            else:
                self.future[x][y] = 0

    def cycle_one_generation(self) -> None:
        for i in range(63):
            for j in range(127):
                self.update_cell_survival(i, j)
        self.grid = deepcopy(self.future)

class Game:
    def __init__(self):
        self.display_surface = pygame.display.set_mode((1024, 512))
        pygame.display.set_caption("John Conway's Game Of Life!")
        self.scaling_dimensions: list = [int(pow(2, i)) for i in list(range(3, 8))]
        self.simulation: Grid = Grid()
        self.dimension: int = 0
        self.pos_x, self.pos_y = 0, 0
        self.automated_simulation()

    def draw_grid(self) -> None:
        self.display_surface.fill((0, 0, 0, 255))
        visible_grid: list = self.simulation.get_visible_grid_portion()
        for i in range(len(visible_grid)):
            for j in range(len(visible_grid[i])):
                self.update_dimensions()
                if visible_grid[i][j]:
                    pygame.draw.rect(
                        self.display_surface,
                        (255, 255, 255, 255),
                        [self.dimension * j, self.dimension * i] + [self.dimension] * 2,
                        0
                    )
                pygame.draw.rect(
                    self.display_surface,
                    (83, 83, 83, 255),
                    [self.dimension * j, self.dimension * i] + [self.dimension] * 2, 1
                )
        pygame.display.update()

    def update_dimensions(self):
        self.dimension = self.scaling_dimensions[self.simulation.zoom_level]

    def approximate_mouse_position(self) -> None:
        self.update_dimensions()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.pos_x = (mouse_x - mouse_x % self.dimension) // self.dimension
        self.pos_y = (mouse_y - mouse_y % self.dimension) // self.dimension

    def modify_grid(self) -> None:
        self.update_dimensions()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    quit(0)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.approximate_mouse_position()
                    offx: int = self.simulation.zoom_levels[0][self.simulation.zoom_level][0]
                    offy: int = self.simulation.zoom_levels[1][self.simulation.zoom_level][0]
                    self.simulation.grid[self.pos_y + offy][self.pos_x + offx + offy // 2] = (
                        int(not self.simulation.grid[self.pos_y + offy][self.pos_x + offx + offy // 2])
                    )
                    self.draw_grid()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    return

    def automated_simulation(self) -> None:
        self.draw_grid()
        self.modify_grid()
        pausing: bool = False
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    quit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        pausing = not pausing
                    elif event.key == pygame.K_ESCAPE:
                        return
                    elif event.key == pygame.K_UP:
                        self.simulation.zoom_level += 1 if self.simulation.zoom_level < 4 else 0
                    elif event.key == pygame.K_DOWN:
                        self.simulation.zoom_level -= 1 if self.simulation.zoom_level > 0 else 0

            if not pausing:
                self.simulation.cycle_one_generation()
                self.draw_grid()
                sleep(0.01)
            else:
                self.modify_grid()
                pausing = False

game: Game = Game()