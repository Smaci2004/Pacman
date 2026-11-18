import random
from typing import Optional

import pygame

from maze.utils import MOVES, bfs_next_step, neighbors
from services.resources import asset_path

Cell = tuple[int, int]

CHASE = "chase"
FRIGHTENED = "frightened"
EATEN = "eaten"

DIRECT = "direct"
AMBUSH = "ambush"
FLANK = "flank"
SHY = "shy"

AMBUSH_LEAD = 4
FLANK_LEAD = 6
SHY_DISTANCE = 6


class Ghost:

    def __init__(
        self,
        maze: list[list[int]],
        color: str,
        home: Cell,
        tile_size: int = 32,
        personality: str = DIRECT,
    ) -> None:
        self.color = color
        self.home = home
        self.tile_size = tile_size
        self.personality = personality
        self.speed = max(2, tile_size // 18)
        self._load_sprites()
        self.reset(maze)

    def _load_sprites(self) -> None:
        size = int(self.tile_size * 0.65)
        self.sprites: dict[str, list[pygame.Surface]] = {}
        for facing in ("up", "down", "left", "right"):
            frames = []
            for suffix in ("", "2"):
                name = f"{self.color}_{facing}{suffix}.png"
                img = pygame.image.load(
                    asset_path(name)
                ).convert_alpha()
                frames.append(pygame.transform.scale(img, (size, size)))
            self.sprites[facing] = frames

        self.frightened = [
            pygame.transform.scale(
                pygame.image.load(
                    asset_path(n)
                ).convert_alpha(),
                (size, size),
            )
            for n in ("edible.png", "edible2.png")
        ]

    def reset(self, maze: list[list[int]]) -> None:
        self.maze = maze
        self.grid_x, self.grid_y = self.home
        self.x = self.grid_x * self.tile_size + self.tile_size // 2
        self.y = self.grid_y * self.tile_size + self.tile_size // 2
        self.state = CHASE
        self.facing = "left"
        self.frame = 0
        self.frame_timer = 0.0
        self.eaten_timer = 0.0
        self.target: Optional[Cell] = None

    def set_frightened(self, frightened: bool) -> None:
        if self.state == EATEN:
            return
        self.state = FRIGHTENED if frightened else CHASE

    def get_eaten(self, respawn_seconds: float) -> None:
        self.state = EATEN
        self.eaten_timer = respawn_seconds

    def _centered(self) -> bool:
        cx = self.grid_x * self.tile_size + self.tile_size // 2
        cy = self.grid_y * self.tile_size + self.tile_size // 2
        return self.x == cx and self.y == cy

    def _project(
        self,
        pac_cell: Cell,
        pac_dir: Optional[int],
        lead: int,
    ) -> Cell:
        rows, cols = len(self.maze), len(self.maze[0])
        dx, dy = MOVES.get(pac_dir, (0, 0)) if pac_dir else (0, 0)
        tx = max(0, min(cols - 1, pac_cell[0] + dx * lead))
        ty = max(0, min(rows - 1, pac_cell[1] + dy * lead))
        return (tx, ty)

    def _choose_target(
        self,
        pac_cell: Cell,
        pac_dir: Optional[int] = None,
        scatter: bool = False,
    ) -> Cell:
        if self.state == EATEN:
            return self.home

        if self.state == FRIGHTENED:
            options = neighbors(self.maze, self.grid_x, self.grid_y)
            if options:
                return max(
                    options,
                    key=lambda c: abs(c[0] - pac_cell[0])
                    + abs(c[1] - pac_cell[1]),
                )
            return (self.grid_x, self.grid_y)

        if scatter:
            return self.home

        if self.personality == AMBUSH:
            return self._project(pac_cell, pac_dir, AMBUSH_LEAD)

        if self.personality == FLANK:
            return self._project(pac_cell, pac_dir, FLANK_LEAD)

        if self.personality == SHY:
            distance = (
                abs(self.grid_x - pac_cell[0])
                + abs(self.grid_y - pac_cell[1])
            )
            return self.home if distance <= SHY_DISTANCE else pac_cell

        return pac_cell

    def update(
        self,
        pac_cell: Cell,
        dt: float,
        frozen: bool = False,
        pac_dir: Optional[int] = None,
        scatter: bool = False,
    ) -> None:
        self._animate(dt)

        if self.state == EATEN and (self.grid_x, self.grid_y) == self.home:
            self.eaten_timer -= dt
            if self.eaten_timer <= 0:
                self.state = CHASE
            return

        if frozen and self.state != EATEN:
            return

        if self._centered():
            target = self._choose_target(pac_cell, pac_dir, scatter)
            step = bfs_next_step(
                self.maze, (self.grid_x, self.grid_y), target
            )

            if step is None:
                opts = neighbors(self.maze, self.grid_x, self.grid_y)
                step = random.choice(opts) if opts else None

            self.target = step

        if self.target is None:
            return

        self._step_toward(self.target)

    def _step_toward(self, cell: Cell) -> None:
        tx = cell[0] * self.tile_size + self.tile_size // 2
        ty = cell[1] * self.tile_size + self.tile_size // 2
        speed = self.speed * (2 if self.state == EATEN else 1)

        if self.x < tx:
            self.x = min(tx, self.x + speed)
            self.facing = "right"
        elif self.x > tx:
            self.x = max(tx, self.x - speed)
            self.facing = "left"
        elif self.y < ty:
            self.y = min(ty, self.y + speed)
            self.facing = "down"
        elif self.y > ty:
            self.y = max(ty, self.y - speed)
            self.facing = "up"

        if self.x == tx and self.y == ty:
            self.grid_x, self.grid_y = cell

    def _animate(self, dt: float) -> None:
        self.frame_timer += dt

        if self.frame_timer >= 0.15:
            self.frame_timer = 0.0
            self.frame = 1 - self.frame

    def draw(self, screen: pygame.Surface, ox: int, oy: int) -> None:
        if self.state in (FRIGHTENED, EATEN):
            image = self.frightened[self.frame]
        else:
            image = self.sprites[self.facing][self.frame]

        rect = image.get_rect(
            center=(int(self.x + ox), int(self.y + oy))
        )
        screen.blit(image, rect.topleft)


def make_ghosts(
    maze: list[list[int]],
    corners: list[Cell],
    tile_size: int = 32,
) -> list[Ghost]:
    profiles = [
        ("red", DIRECT),
        ("pink", AMBUSH),
        ("cyan", FLANK),
        ("yellow", SHY),
    ]

    ghosts: list[Ghost] = []

    for (color, personality), corner in zip(profiles, corners):
        ghosts.append(
            Ghost(maze, color, corner, tile_size, personality)
        )

    return ghosts
