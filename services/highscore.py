import json
import os
from typing import Any

MAX_ENTRIES = 10
MAX_NAME_LENGTH = 10


def sanitize_name(raw: str) -> str:
    cleaned = "".join(c for c in raw if c.isalnum() or c == " ")
    cleaned = cleaned.strip()[:MAX_NAME_LENGTH]
    return cleaned or "PLAYER"


class HighscoreManager:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.scores: list[dict[str, Any]] = []
        self.load()

    def load(self) -> None:
        if not os.path.exists(self.filename):
            self.scores = []
            return
        try:
            with open(self.filename, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[highscore] could not read {self.filename}: {exc}")
            self.scores = []
            return
        self.scores = self._coerce(data)
        self._sort_and_trim()

    def _coerce(self, data: Any) -> list[dict[str, Any]]:
        if not isinstance(data, list):
            return []
        clean: list[dict[str, Any]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            name = sanitize_name(str(item.get("name", "")))
            try:
                score = int(item.get("score", 0))
            except (TypeError, ValueError):
                continue
            if score < 0:
                continue
            clean.append({"name": name, "score": score})
        return clean

    def _sort_and_trim(self) -> None:
        self.scores.sort(key=lambda e: e["score"], reverse=True)
        self.scores = self.scores[:MAX_ENTRIES]

    def qualifies(self, score: int) -> bool:
        if score <= 0:
            return False
        if len(self.scores) < MAX_ENTRIES:
            return True
        return score > int(self.scores[-1]["score"])

    def add(self, name: str, score: int) -> None:
        score = max(0, int(score))
        self.scores.append(
            {"name": sanitize_name(name), "score": score}
        )
        self._sort_and_trim()
        self.save()

    def save(self) -> None:
        try:
            with open(self.filename, "w", encoding="utf-8") as handle:
                json.dump(self.scores, handle, indent=2)
        except OSError as exc:
            print(f"[highscore] could not write {self.filename}: {exc}")

    def top(self, limit: int = MAX_ENTRIES) -> list[dict[str, Any]]:
        return self.scores[:limit]
