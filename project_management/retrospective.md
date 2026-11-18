# Retrospective: Blocking Points & Resolutions

## 1. Maze generator hangs on some seeds
**Problem.** The assigned package's shortest-path search becomes very
slow for certain random seeds, which would freeze level generation.
**Resolution.** Wrapped each generation attempt in a SIGALRM timeout and
retry with fresh seeds, raising a clean `MazeError` only if every attempt
fails. The game then ends the run gracefully rather than freezing.

## 2. Centre/corner cells can be solid blocks
**Problem.** The generator embeds a solid "42" shape near the centre, so
the exact centre or a corner may be unusable for spawning.
**Resolution.** `maze_utils` resolves the nearest open cell to any target
via a small BFS, so Pac-Man, ghosts and pellets always land on valid
corridors.

## 3. Jittery ghost movement
**Problem.** Recomputing the BFS target every frame made ghosts
oscillate at junctions.
**Resolution.** Ghosts only re-decide their next step when sitting
exactly on a cell centre, producing smooth, classic movement.

## 4. mypy strictness on the optional external import
**Problem.** The fallback import of the maze package tripped mypy's
unused-`type: ignore` check once the package was installed.
**Resolution.** Imported under an alias assigned to an `Any`-typed name,
keeping the safe fallback without a stray ignore comment.

## What went well
- Isolating geometry in one module made the entities small and the whole
  game easy to reason about and test headlessly.
- Defensive I/O meant no crash path remained for config or save files.

## What we'd do next with more time
- Add automated `pytest` unit tests for `maze_utils` and `highscore`.
- Tune per-ghost personalities (distinct chase targets like the original).
