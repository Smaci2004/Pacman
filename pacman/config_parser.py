import json
import re
from typing import Any


DEFAULTS: dict[str, Any] = {
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
    "level_max_time": 60,
}


BOUNDS: dict[str, tuple[int, int]] = {
    "levels": (1, 99),
    "width": (7, 15),
    "height": (7, 15),
    "lives": (1, 99),
    "pacgum": (1, 9999),
    "points_per_pacgum": (0, 100000),
    "points_per_super_pacgum": (0, 100000),
    "points_per_ghost": (0, 100000),
    "seed": (0, 2**31 - 1),
    "level_max_time": (5, 9999),
}


class ConfigError(Exception):
    pass


class ConfigParser:

    _COMMENT_RE = re.compile(r"^\s*(#|//)")

    def _strip_comments(self, text: str) -> str:
        kept = [
            line
            for line in text.splitlines()
            if not self._COMMENT_RE.match(line)
        ]
        return "\n".join(kept)

    def load_file(self, filename: str) -> dict[str, Any]:
        try:
            with open(filename, "r", encoding="utf-8") as handle:
                raw = handle.read()
        except FileNotFoundError as exc:
            raise ConfigError(
                f"Config file not found: {filename}"
            ) from exc
        except OSError as exc:
            raise ConfigError(
                f"Could not read config file {filename}: {exc}"
            ) from exc

        try:
            data = json.loads(self._strip_comments(raw))
        except json.JSONDecodeError as exc:
            raise ConfigError(
                f"Invalid JSON in {filename}: {exc}"
            ) from exc

        if not isinstance(data, dict):
            raise ConfigError("Config root must be a JSON object.")

        return data

    def _clamp_int(self, key: str, value: Any) -> int:
        default = int(DEFAULTS[key])

        try:
            number = int(value)
        except (TypeError, ValueError):
            print(
                f"[config] '{key}' is not an int; using {default}."
            )
            return default

        low, high = BOUNDS[key]

        if number < low or number > high:
            clamped = max(low, min(high, number))
            print(
                f"[config] '{key}'={number} out of range "
                f"[{low}, {high}]; clamped to {clamped}."
            )
            return clamped

        return number

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        config: dict[str, Any] = {}

        name = data.get(
            "highscore_filename",
            DEFAULTS["highscore_filename"],
        )

        if not isinstance(name, str) or not name.strip():
            print(
                "[config] invalid 'highscore_filename'; using default."
            )
            name = DEFAULTS["highscore_filename"]

        config["highscore_filename"] = name

        for key in BOUNDS:
            config[key] = self._clamp_int(
                key,
                data.get(key, DEFAULTS[key]),
            )

        for unknown in set(data) - set(DEFAULTS):
            print(f"[config] ignoring unknown key '{unknown}'.")

        return config

    def parse(self, filename: str) -> dict[str, Any]:
        return self.validate(self.load_file(filename))
