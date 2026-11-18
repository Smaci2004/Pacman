# Acceptance Test Plan

Tested manually and with a headless run (SDL dummy driver).

| # | Feature | Test | Result |
| - | ------- | ---- | ------ |
| 1 | One JSON argument | Run with 0 or 2 args | Usage message, no traceback |
| 2 | Config comments `#` and `//` | Parse `config.json` | OK |
| 3 | Invalid or missing values | Bad config | Clamped, logged, no crash |
| 4 | Unknown keys | Extra key | Ignored |
| 5 | Level 1 fixed seed | Generate twice with seed 42 | Identical mazes |
| 6 | Later levels random | Generate levels 2-5 | Different mazes |
| 7 | Slow seed | Many seeds | Timeout caught, retried |
| 8 | Movement limited to corridors | Drive into walls | Blocked |
| 9 | Arrows and WASD | Press both | Both work |
| 10 | Pacgum scoring | Eat a pacgum | Score += `points_per_pacgum` |
| 11 | Super-pacgum | Eat one | Ghosts edible for 7 s |
| 12 | Edible ghost | Touch it | Score += `points_per_ghost`, ghost respawns |
| 13 | Ghost kills player | Touch a chasing ghost | Life lost, respawn at centre |
| 14 | Game over | Lose all lives | Game Over screen |
| 15 | Level cleared | Eat every pellet | Next level |
| 16 | Victory | Clear the last level | Victory screen |
| 17 | Level time limit | Let the timer reach 0 | Game Over (all lives lost at once, see kanban) |
| 18 | Pause and resume | Press `P` | OK |
| 19 | Highscore persistence | Add a score, restart | Score still there |
| 20 | Name validation | `Bob!!`, 20 characters | `Bob`, truncated to 10 |
| 21 | Top 10 | Add many scores | 10 kept, sorted |
| 22 | Corrupt highscore file | Broken JSON | Empty table, no crash |
| 23 | Cheats | Toggle each | OK |
| 24 | HUD | Play | Score, lives, level, time, cheats shown |

## Bugs found and fixed

- Ghost collision could be missed when two fast movers swapped cells between
  frames: added a pixel-distance fallback.
- A string literal was used for the frightened state: replaced by the
  `FRIGHTENED` constant.

## Known issue

- When the level timer reaches 0, a life is lost but the timer is not reset,
  so all lives are lost in a few frames.