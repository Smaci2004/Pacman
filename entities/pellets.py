import random
from typing import Optional

import pygame

from maze.utils import is_open, corner_cells, center_cell
from services.resources import asset_path

Cell = tuple[int, int]


class PelletManager:

    def __init__(
        self,
        maze: list[list[int]],
        pacgum_count: int = 42,
        points_pacgum: int = 10,
        points_super: int = 50,
        tile_size: int = 32,
        seed: Optional[int] = None,
    ) -> None:
        self.tile_size = tile_size
        self.points_pacgum = points_pacgum
        self.points_super = points_super
        self.pacgum_count = pacgum_count
        self._rng = random.Random(seed)

        power = pygame.image.load(
            asset_path("power_pellet.png")
        ).convert_alpha()
        self.power_image = pygame.transform.scale(
            power, (int(tile_size * 0.65), int(tile_size * 0.65))
        )

        normal = pygame.image.load(
            asset_path("pellet.png")
        ).convert_alpha()
        self.normal_image = pygame.transform.scale(
            normal, (int(tile_size * 0.35), int(tile_size * 0.35))
        )

        self.populate(maze)

    def populate(self, maze: list[list[int]]) -> None:
        self.power_pellets: set[Cell] = set(corner_cells(maze))
        spawn = center_cell(maze)

        available = [
            (x, y)
            for y in range(len(maze))
            for x in range(len(maze[0]))
            if is_open(maze, x, y)
            and (x, y) not in self.power_pellets
            and (x, y) != spawn
        ]

        count = min(self.pacgum_count, len(available))
        self.normal_pellets: set[Cell] = set(
            self._rng.sample(available, count)
        )

    @property
    def remaining(self) -> int:
        return len(self.normal_pellets) + len(self.power_pellets)

    def check_collision(self, cell: Cell) -> tuple[int, bool]:
        if cell in self.normal_pellets:
            self.normal_pellets.discard(cell)
            return self.points_pacgum, False

        if cell in self.power_pellets:
            self.power_pellets.discard(cell)
            return self.points_super, True

        return 0, False

    def _blit(
        self,
        screen: pygame.Surface,
        image: pygame.Surface,
        cell: Cell,
        ox: int,
        oy: int,
    ) -> None:
        cx = cell[0] * self.tile_size + self.tile_size // 2 + ox
        cy = cell[1] * self.tile_size + self.tile_size // 2 + oy
        rect = image.get_rect(center=(int(cx), int(cy)))
        screen.blit(image, rect.topleft)

    def draw(self, screen: pygame.Surface, ox: int, oy: int) -> None:
        for cell in self.normal_pellets:
            self._blit(screen, self.normal_image, cell, ox, oy)

        for cell in self.power_pellets:
            self._blit(screen, self.power_image, cell, ox, oy)
