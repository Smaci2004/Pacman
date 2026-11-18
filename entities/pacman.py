from typing import Optional

import pygame

from maze.utils import MOVES, NORTH, EAST, SOUTH, WEST, can_move, center_cell
from services.resources import asset_path


class Pacman:

    def __init__(
        self,
        maze: list[list[int]],
        tile_size: int = 32,
        image_path: Optional[str] = None,
    ) -> None:
        self.tile_size = tile_size
        path = image_path or asset_path("pacman.png")
        base = pygame.image.load(path).convert_alpha()
        sprite = int(tile_size * 0.65)
        self.image = pygame.transform.scale(base, (sprite, sprite))

        self.current_dir: Optional[int] = None
        self.next_dir: Optional[int] = None
        self.facing = EAST
        self._face_left = False
        self.base_speed = max(2, tile_size // 16)
        self.speed = self.base_speed
        self.reset(maze)

    def reset(self, maze: list[list[int]]) -> None:
        self.maze = maze
        self.rows = len(maze)
        self.cols = len(maze[0])
        self.grid_x, self.grid_y = center_cell(maze)
        self.x = self.grid_x * self.tile_size + self.tile_size // 2
        self.y = self.grid_y * self.tile_size + self.tile_size // 2
        self.current_dir = None
        self.next_dir = None

    def set_direction(self, direction: int) -> None:
        self.next_dir = direction

    def _at_center(self) -> tuple[int, int]:
        cx = self.grid_x * self.tile_size + self.tile_size // 2
        cy = self.grid_y * self.tile_size + self.tile_size // 2
        return cx, cy

    def update(self) -> None:
        if self.current_dir:
            dx, dy = MOVES[self.current_dir]
            cx, cy = self._at_center()
            overshot = (
                (dx > 0 and self.x <= cx < self.x + self.speed)
                or (dx < 0 and self.x >= cx > self.x - self.speed)
                or (dy > 0 and self.y <= cy < self.y + self.speed)
                or (dy < 0 and self.y >= cy > self.y - self.speed)
            )
            if overshot:
                self.x, self.y = cx, cy
                if self.next_dir and can_move(
                    self.maze, self.grid_x, self.grid_y, self.next_dir
                ):
                    self.current_dir = self.next_dir
                    self.next_dir = None
                    self.facing = self.current_dir
                elif not can_move(
                    self.maze, self.grid_x, self.grid_y, self.current_dir
                ):
                    self.current_dir = None
        elif self.next_dir and can_move(
            self.maze, self.grid_x, self.grid_y, self.next_dir
        ):
            self.current_dir = self.next_dir
            self.next_dir = None
            self.facing = self.current_dir

        if self.current_dir:
            dx, dy = MOVES[self.current_dir]
            self.x += dx * self.speed
            self.y += dy * self.speed
            self.grid_x = int(self.x // self.tile_size)
            self.grid_y = int(self.y // self.tile_size)

    def draw(self, screen: pygame.Surface, ox: int, oy: int) -> None:
        face = self.facing
        if face == EAST:
            self._face_left = False
        elif face == WEST:
            self._face_left = True

        face_left = self._face_left

        if face_left:
            image = self.image
        else:
            image = pygame.transform.flip(self.image, True, False)

        rect = image.get_rect(
            center=(int(self.x + ox), int(self.y + oy))
        )
        screen.blit(image, rect.topleft)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        keymap = {
            pygame.K_w: NORTH,
            pygame.K_UP: NORTH,
            pygame.K_d: EAST,
            pygame.K_RIGHT: EAST,
            pygame.K_s: SOUTH,
            pygame.K_DOWN: SOUTH,
            pygame.K_a: WEST,
            pygame.K_LEFT: WEST,
        }

        if event.key in keymap:
            self.set_direction(keymap[event.key])
