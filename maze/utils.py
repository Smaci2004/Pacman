from collections import deque
from typing import Optional

NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8
SOLID = 15

MOVES: dict[int, tuple[int, int]] = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0),
}

Cell = tuple[int, int]


def in_bounds(maze: list[list[int]], x: int, y: int) -> bool:
    return 0 <= y < len(maze) and 0 <= x < len(maze[0])


def is_open(maze: list[list[int]], x: int, y: int) -> bool:
    return in_bounds(maze, x, y) and maze[y][x] != SOLID


def can_move(
    maze: list[list[int]],
    x: int,
    y: int,
    direction: int,
) -> bool:
    if not in_bounds(maze, x, y):
        return False

    if maze[y][x] & direction:
        return False

    dx, dy = MOVES[direction]
    return is_open(maze, x + dx, y + dy)


def neighbors(maze: list[list[int]], x: int, y: int) -> list[Cell]:
    result: list[Cell] = []

    for direction, (dx, dy) in MOVES.items():
        if can_move(maze, x, y, direction):
            result.append((x + dx, y + dy))

    return result


def bfs_next_step(
    maze: list[list[int]],
    start: Cell,
    goal: Cell,
) -> Optional[Cell]:
    if start == goal:
        return None

    queue: deque[Cell] = deque([start])
    came_from: dict[Cell, Optional[Cell]] = {start: None}

    while queue:
        current = queue.popleft()

        if current == goal:
            break

        for nxt in neighbors(maze, current[0], current[1]):
            if nxt not in came_from:
                came_from[nxt] = current
                queue.append(nxt)

    if goal not in came_from:
        return None

    node: Cell = goal
    parent = came_from[node]

    while parent is not None and parent != start:
        node = parent
        parent = came_from[node]

    return node


def corner_cells(maze: list[list[int]]) -> list[Cell]:
    rows, cols = len(maze), len(maze[0])
    targets = [
        (0, 0),
        (cols - 1, 0),
        (0, rows - 1),
        (cols - 1, rows - 1),
    ]

    found: list[Cell] = []

    for tx, ty in targets:
        found.append(_nearest_open(maze, tx, ty))

    return found


def _nearest_open(maze: list[list[int]], tx: int, ty: int) -> Cell:
    rows, cols = len(maze), len(maze[0])
    queue: deque[Cell] = deque([(tx, ty)])
    seen = {(tx, ty)}

    while queue:
        x, y = queue.popleft()

        if is_open(maze, x, y):
            return (x, y)

        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy

            if (
                0 <= nx < cols
                and 0 <= ny < rows
                and (nx, ny) not in seen
            ):
                seen.add((nx, ny))
                queue.append((nx, ny))

    return (tx, ty)


def center_cell(maze: list[list[int]]) -> Cell:
    cols, rows = len(maze[0]), len(maze)
    return _nearest_open(maze, cols // 2, rows // 2)
