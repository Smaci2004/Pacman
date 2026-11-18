# Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
| Maze package interface differs from expected | Medium | High | Everything isolated in `maze/loader.py` |
| Generator very slow for some seeds | Medium | High | 1 s timeout per attempt, up to 8 retries, clean `MazeError` |
| Maze has a solid block at the centre or a corner | Medium | Medium | Nearest-open-cell search in `maze/utils.py` |
| Faulty config crashes the game | Medium | High | Clamping, defaults, unknown keys ignored, clear messages |
| Corrupt or missing highscore file | Medium | Medium | All file I/O wrapped; empty table on failure |
| Ghosts make review tedious | Low | Medium | Cheat mode (invincible, freeze, skip, extra life) |
| Packaging misses assets | Low | Medium | `pacman.spec` lists `assets/`, `config.json` and the maze package |
| Style or type regressions | Medium | Low | `make lint` before delivery |

## Residual risk

The reviewer's reinstalled maze package may behave differently. Changes would
be limited to `maze/loader.py` and `maze/utils.py`.