import random
import signal
from types import FrameType
from typing import Any, Optional

try:
    from mazegenerator.mazegenerator import MazeGenerator as _MazeGen
    MazeGenerator: Any = _MazeGen
except ImportError:
    MazeGenerator = None


class MazeError(Exception):
    pass


class _Timeout(Exception):
    pass


def _alarm(signum: int, frame: Optional[FrameType]) -> None:
    raise _Timeout()


class MazeLoader:

    TIMEOUT_SECONDS = 1
    MAX_ATTEMPTS = 8

    def __init__(self, width: int, height: int, base_seed: int) -> None:
        self.width = width
        self.height = height
        self.base_seed = base_seed

    def _build(self, seed: int) -> list[list[int]]:
        if MazeGenerator is None:
            raise MazeError(
                "The A-Maze-ing 'mazegenerator' package is not installed."
            )

        use_alarm = hasattr(signal, "SIGALRM")
        previous = None

        if use_alarm:
            previous = signal.signal(signal.SIGALRM, _alarm)
            signal.setitimer(signal.ITIMER_REAL, self.TIMEOUT_SECONDS)

        try:
            generator: Any = MazeGenerator(
                size=(self.width, self.height),
                perfect=False,
                seed=seed,
            )
            raw_maze = generator.maze

            if not isinstance(raw_maze, list):
                raise MazeError(
                    "Maze generator returned an invalid grid."
                )

            maze: list[list[int]] = []

            for row in raw_maze:
                if not isinstance(row, list):
                    raise MazeError(
                        "Maze generator returned an invalid row."
                    )

                if not all(isinstance(cell, int) for cell in row):
                    raise MazeError(
                        "Maze generator returned invalid cell values."
                    )

                maze.append(row)

        except _Timeout as exc:
            raise MazeError(
                f"Maze generation timed out for seed {seed}."
            ) from exc
        except MazeError:
            raise
        except Exception as exc:
            raise MazeError(
                f"Maze generation failed: {exc}"
            ) from exc
        finally:
            if use_alarm:
                signal.setitimer(signal.ITIMER_REAL, 0)

                if previous is not None:
                    signal.signal(signal.SIGALRM, previous)

        if not maze or not maze[0]:
            raise MazeError("Maze generator returned an empty grid.")

        return maze

    def generate(self, level_index: int) -> list[list[int]]:
        if MazeGenerator is None:
            raise MazeError(
                "The A-Maze-ing 'mazegenerator' package is not installed. "
                "Run 'make install' (or pip install the wheel in utils/)."
            )

        if level_index == 0:
            first = self.base_seed if self.base_seed > 0 else 1
        else:
            first = random.randint(1, 2**31 - 1)

        last_error: Optional[MazeError] = None

        for attempt in range(self.MAX_ATTEMPTS):
            seed = (
                first
                if attempt == 0
                else random.randint(1, 2**31 - 1)
            )

            try:
                return self._build(seed)
            except MazeError as exc:
                last_error = exc
                print(f"[maze] {exc} Retrying...")

        raise MazeError(
            f"Could not generate a maze after {self.MAX_ATTEMPTS} attempts: "
            f"{last_error}"
        )
