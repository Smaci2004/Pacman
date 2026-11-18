import pygame

from maze.utils import NORTH, EAST, SOUTH, WEST, SOLID


class MazeRenderer:

    def __init__(self, tile_size: int = 32) -> None:
        self.tile_size = tile_size
        self.wall_color = (255, 255, 255)
        self.fill_color = (138, 0, 196)
        self.wall_thickness = max(1, tile_size // 20)

    @staticmethod
    def fit_tile_size(
        maze: list[list[int]],
        screen_w: int,
        screen_h: int,
        hud_height: int = 60,
        margin: int = 20,
    ) -> int:
        cols, rows = len(maze[0]), len(maze)
        usable_w = screen_w - 2 * margin
        usable_h = screen_h - hud_height - 2 * margin
        return max(8, min(usable_w // cols, usable_h // rows))

    def get_offsets(
        self,
        screen: pygame.Surface,
        maze: list[list[int]],
        hud_height: int = 60,
    ) -> tuple[int, int]:
        maze_w = len(maze[0]) * self.tile_size
        maze_h = len(maze) * self.tile_size
        ox = (screen.get_width() - maze_w) // 2
        oy = hud_height + (
            screen.get_height() - hud_height - maze_h
        ) // 2
        return ox, oy

    def draw(
        self,
        screen: pygame.Surface,
        maze: list[list[int]],
        ox: int,
        oy: int,
    ) -> None:
        ts = self.tile_size

        for row_idx, row in enumerate(maze):
            for col_idx, value in enumerate(row):
                if value == SOLID:
                    rect = pygame.Rect(
                        col_idx * ts + ox, row_idx * ts + oy, ts, ts
                    )
                    pygame.draw.rect(screen, self.fill_color, rect)

        for row_idx, row in enumerate(maze):
            for col_idx, value in enumerate(row):
                x = col_idx * ts + ox
                y = row_idx * ts + oy
                tl, tr = (x, y), (x + ts, y)
                bl, br = (x, y + ts), (x + ts, y + ts)

                if value & NORTH:
                    self._line(screen, tl, tr)
                if value & EAST:
                    self._line(screen, tr, br)
                if value & SOUTH:
                    self._line(screen, bl, br)
                if value & WEST:
                    self._line(screen, tl, bl)

    def _line(
        self,
        screen: pygame.Surface,
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> None:
        pygame.draw.line(
            screen, self.wall_color, start, end, self.wall_thickness
        )
