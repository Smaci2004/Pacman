# Timeline & Progress

Dates are in `[...]`: fill them in from your real work (the Git history
should match).

| # | Milestone | Planned | Actual | Status |
| - | --------- | ------- | ------ | ------ |
| 1 | Skeleton, config parser, maze loader | Day 1 | [date] | Done |
| 2 | Maze rendering, Pac-Man movement | Day 1-2 | [date] | Done |
| 3 | Pellets | Day 2 | [date] | Done |
| 4 | Ghost AI | Day 2-3 | [date] | Done |
| 5 | State machine: lives, timer, levels | Day 3 | [date] | Done |
| 6 | UI: menu, HUD, pause, end screens | Day 3-4 | [date] | Done |
| 7 | Highscores | Day 4 | [date] | Done |
| 8 | Cheat mode | Day 4 | [date] | Done |
| 9 | flake8 + mypy clean | Day 4 | [date] | Done |
| 10 | Makefile, `.gitignore`, requirements | Day 5 | [date] | Done |
| 11 | Packaging and Itch.io upload | Day 5 | [date] | [Done / In progress] |
| 12 | README and project management docs | Day 5 | [date] | Done |

## Deviations

- Ghost AI took longer than planned: ghosts jittered at junctions until they
  were made to re-decide only at cell centres.
- Unplanned: a timeout and retry around the maze generator (some seeds hang).