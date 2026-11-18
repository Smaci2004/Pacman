import os
import sys


def _base_dir() -> str:
    bundled = getattr(sys, "_MEIPASS", None)
    if bundled:
        return str(bundled)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def asset_path(name: str) -> str:
    return os.path.join(_base_dir(), "assets", name)
