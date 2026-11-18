# Pac-Man

<img width="1920" height="1200" alt="pac1" src="https://github.com/user-attachments/assets/a895ff3e-b931-4269-8333-5334ae1f7a1b" />

## Description

A complete Pac-Man clone written in Python 3.10+ with object-oriented
programming and `pygame`. The player moves through a maze, eats pacgums and
avoids four ghosts. Eating a super-pacgum makes the ghosts edible for a short
time. The game has 10 levels by default, each with its own maze and time limit,
a persistent top-10 highscore table, a configuration file and a cheat mode for
peer review.

The goal is to practise object-oriented design, a modular architecture, robust
error handling, integration of an external package (the assigned A-Maze-ing
generator), project management and packaging.

## Instructions

Requirements: Python 3.10+, the assigned A-Maze-ing wheel (in `utils/`) and
`pygame` (both installed by `make install`).

```console
$> make install
$> make run
# or directly:
$> python3 pac-man.py config.json
```

The program takes exactly one argument: a JSON configuration file. Other rules:
`make debug` (pdb), `make clean`, `make lint`, `make lint-strict`.

Controls: arrow keys or `W` `A` `S` `D` to move, `P` pause, `ESC` back to the
menu. Main menu: `SPACE` start, `I` instructions, `H` highscores, `ESC` exit.

Cheat mode (during a game, shown in the HUD): `C` invincibility, `F` freeze
ghosts, `N` skip level, `L` extra life.

## Resources

- pygame documentation: https://www.pygame.org/docs/
- *The Pac-Man Dossier* (original ghost behaviour): https://pacman.holenet.info/
- Python documentation (`json`, `re`, `signal`, `typing`): https://docs.python.org/3/
- Breadth-first search on grid graphs (standard references)
- PEP 8, PEP 257, flake8 and mypy documentation
- PyInstaller documentation: https://pyinstaller.org/

### Use of AI

AI (Claude) was used as an assistant; every suggestion was reviewed and tested
by the team before being kept.

| Task | Where |
| ---- | ----- |
| Error handling around the maze package (timeout and retry) | `maze/loader.py` |
| Config and highscore file I/O hardening | `pacman/config_parser.py`, `services/highscore.py` |
| Documentation and packaging drafts | `README.md`, `project_management/`, `pacman.spec`, `build_package.sh` |

## Configuration

JSON file with comments: lines starting with `#` or `//` are ignored. All keys
are optional. Unknown keys are ignored, and missing or invalid values fall back
to the defaults (or are clamped to the allowed range) with a logged message.

```jsonc
# config.json
{
    "highscore_filename": "highscores.json",
    "levels": 10,
    "width": 15,
    "height": 15,
    "lives": 3,
    "pacgum": 42,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 90
}
```

| Key | Default | Meaning |
| --- | ------- | ------- |
| `highscore_filename` | `highscores.json` | Highscore file |
| `levels` | `10` | Number of levels |
| `width`, `height` | `15`, `15` | Maze size in cells (7 – 15) |
| `lives` | `3` | Starting lives |
| `pacgum` | `42` | Pacgums per level |
| `points_per_pacgum` | `10` | Score per pacgum |
| `points_per_super_pacgum` | `50` | Score per super-pacgum |
| `points_per_ghost` | `200` | Score per edible ghost |
| `seed` | `42` | Seed of the first level's maze |
| `level_max_time` | `90` | Time limit per level, in seconds |

## Highscore

- Stored as a JSON list of `{"name": ..., "score": ...}` in the file given by
  `highscore_filename`, loaded at start-up and saved when a score is added.
- Only the top 10 are kept, sorted from best to worst.
- Names: max 10 characters, alphanumeric and spaces only. Scores: non-negative
  integers.
- At the end of a game (win or lose), the player enters a name if the score
  enters the top 10. Highscores are displayed in the main menu.
- A missing, unreadable or corrupt file gives an empty table and a write
  failure is logged, so the game never crashes.

A plain JSON file was chosen because it is human-readable, needs no dependency
and fits the simple name + score record.

## Maze Generation

Mazes come entirely from the assigned A-Maze-ing package (`utils/` wheel), used
as-is. Our loader (`maze/loader.py`) adapts to its interface:

```python
generator = MazeGenerator(size=(width, height), perfect=False, seed=seed)
grid = generator.maze  # list[list[int]]
```

- `perfect=False` produces loops, as required for Pac-Man corridors.
- Level 1 uses the configured `seed`; later levels use random seeds.
- Each cell is a wall bitmask (`1` north, `2` east, `4` south, `8` west,
  `15` solid block).
- Each attempt is limited to 1 second and retried with a new seed up to 8
  times. If all fail, a `MazeError` is raised and handled cleanly.
- The player spawns at the open cell nearest to the centre; ghosts and
  super-pacgums are placed at the open cells nearest to the four corners.

<img width="1917" height="1200" alt="pac2" src="https://github.com/user-attachments/assets/9a1216c5-a433-4f82-9e24-69e59e00c9ff" />

## Implementation

A 60 FPS loop drives a state machine: menu, instructions, highscores, playing,
paused, game over, victory, name entry.

- **Player:** grid-aligned movement with pixel interpolation; the desired
  direction is applied at the next cell centre.
- **Ghosts:** chase, frightened and eaten states. At each cell centre a ghost
  follows a BFS shortest path to its target. Red targets Pac-Man, pink 4 cells
  ahead, cyan 6 cells ahead, and yellow retreats to its corner when closer than
  6 cells. Ghosts alternate scatter (5 s) and chase (20 s), flee for 7 s after
  a super-pacgum, and respawn 6 s after being eaten.
- **Pellets:** super-pacgums in the four corners, pacgums on random open cells.
  A level ends when no pellet remains.
- **Collisions:** same grid cell, with a pixel-distance fallback.
- **Error handling:** config, maze generation and file access degrade
  gracefully; files use context managers; the entry point never shows a
  traceback.

## General Software Architecture

```text
.
├── pac-man.py            Entry point
├── pacman/
│   ├── config_parser.py  ConfigParser: comments, validation, defaults
│   └── game.py           Game: state machine, loop, levels, scoring, cheats
├── maze/
│   ├── loader.py         MazeLoader: adapter for the A-Maze-ing package
│   ├── utils.py          Geometry: walls, moves, BFS, corners, centre
│   └── renderer.py       MazeRenderer: tile sizing and wall drawing
├── entities/
│   ├── pacman.py         Pacman
│   ├── ghost.py          Ghost, make_ghosts
│   └── pellets.py        PelletManager
├── services/
│   ├── highscore.py      HighscoreManager
│   └── resources.py      asset_path
├── screens.py            UI: menus, HUD, pause, end screens
├── assets/               Sprites
├── utils/                A-Maze-ing wheel (unmodified)
└── project_management/
```

```text
pac-man.py ──► ConfigParser ──► config
     └──► Game
            ├── UI
            ├── MazeLoader ──► A-Maze-ing package
            ├── MazeRenderer
            ├── HighscoreManager
            └── per level: Pacman, Ghost × 4, PelletManager
```

`Game` orchestrates everything. `maze/utils.py` is the single source of truth
for walls and legal moves, and `MazeLoader` is the only module that knows the
A-Maze-ing interface.

## Project Management

The project was driven with a timeline, a risk analysis, an
acceptance test plan and a retrospective. All documents are in
[`project_management/`](project_management/).

## Playable build
https://smaci.itch.io/pac-man

<img width="1920" height="1200" alt="pac3" src="https://github.com/user-attachments/assets/33c3a295-b5ff-40e8-8dca-8e3b756e34e5" />
