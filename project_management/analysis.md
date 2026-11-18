# Analysis & Design Choices

## Constraints

- Use the assigned maze package as-is.
- Never crash; clear error messages only.
- flake8 clean, mypy with the mandatory flags.
- Package for a public platform.

## Choices

- **One source of truth for geometry:** `maze/utils.py` defines walls and legal
  moves; Pac-Man, ghosts and pellets all use it.
- **One orchestrator:** `pacman/game.py` (`Game`) runs the state machine;
  entities only update and draw themselves.
- **Adapter for the external package:** `maze/loader.py` is the only module
  that knows the A-Maze-ing interface.
- **Plain JSON highscores:** readable, no dependency, fits a name + score record.
- **Wall bitmask kept:** the generator's 4-bit mask is used directly, with no
  conversion to a tile grid.