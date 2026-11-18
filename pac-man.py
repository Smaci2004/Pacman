import sys

from pacman.config_parser import ConfigError, ConfigParser


def main(argv: list[str]) -> int:
    """Parse the config, start the game, and return an exit code."""
    if len(argv) != 2:
        print("Usage: python3 pac-man.py <config.json>")
        return 1

    try:
        config = ConfigParser().parse(argv[1])
    except ConfigError as exc:
        print(f"Configuration error: {exc}")
        return 1

    # Import pygame-dependent code only after config validation so a
    # bad config fails fast without initialising a display.
    try:
        from pacman.game import Game
    except ImportError as exc:
        print(f"Failed to load game modules: {exc}")
        return 1

    try:
        Game(config).run()
    except KeyboardInterrupt:
        print("\nInterrupted. Bye!")
    except Exception as exc:  # noqa: BLE001 - last-resort safety net
        print(f"Unexpected error: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
