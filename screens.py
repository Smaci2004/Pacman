from typing import Any, Optional

import pygame

YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREY = (170, 170, 170)
RED = (255, 80, 80)
CYAN = (0, 220, 220)
BLACK = (0, 0, 0)


class UI:
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        info = pygame.display.Info()
        self.width = int(info.current_w)
        self.height = int(info.current_h)
        self.screen = pygame.display.set_mode(
            (self.width, self.height), pygame.FULLSCREEN
        )
        pygame.display.set_caption("Pac-Man")
        self.fonts = {
            "title": pygame.font.SysFont("Impact", 130),
            "big": pygame.font.SysFont("Arial", 64, bold=True),
            "menu": pygame.font.SysFont("Arial", 38),
            "hud": pygame.font.SysFont("Arial", 28, bold=True),
            "small": pygame.font.SysFont("Arial", 26),
        }

    def text(
        self,
        content: str,
        font_key: str,
        color: tuple[int, int, int],
        center: tuple[int, int],
    ) -> None:
        surface = self.fonts[font_key].render(content, True, color)
        rect = surface.get_rect(center=center)
        self.screen.blit(surface, rect)

    def _cx(self) -> int:
        return self.width // 2

    def draw_menu(
        self,
        highscores: list[dict[str, Any]],
        maze_error: bool = False,
    ) -> None:
        self.screen.fill(BLACK)
        cx = self._cx()
        self.text("PAC-MAN", "title", YELLOW, (cx, 140))
        if maze_error:
            self.text(
                "Maze package not installed - run 'make install'",
                "small", RED, (cx, 235),
            )
        options = [
            "[SPACE] Start Game",
            "[I] Instructions",
            "[H] Highscores",
            "[ESC] Exit",
        ]
        for i, line in enumerate(options):
            self.text(line, "menu", WHITE, (cx, 300 + i * 55))

        self.text("TOP PLAYERS", "menu", CYAN, (cx, 560))
        if not highscores:
            self.text("No scores yet", "small", GREY, (cx, 610))
        for i, entry in enumerate(highscores[:10]):
            line = f"{i + 1:>2}. {entry['name']:<10} {entry['score']}"
            self.text(line, "small", WHITE, (cx, 610 + i * 34))

    def draw_instructions(self) -> None:
        self.screen.fill(BLACK)
        cx = self._cx()
        self.text("INSTRUCTIONS", "big", YELLOW, (cx, 120))
        lines = [
            "Move: Arrow keys or W A S D",
            "Eat all pacgums to clear a level",
            "Super-pacgums make ghosts edible briefly",
            "Eat edible ghosts for bonus points",
            "Avoid ghosts or you lose a life",
            "P: pause    ESC: back / quit",
            "",
            "Cheats (in game):",
            "  C invincible   F freeze ghosts",
            "  N skip level   L extra life",
            "",
            "Press ESC or SPACE to return",
        ]
        for i, line in enumerate(lines):
            self.text(line, "small", WHITE, (cx, 240 + i * 42))

    def draw_highscores(self, highscores: list[dict[str, Any]]) -> None:
        self.screen.fill(BLACK)
        cx = self._cx()
        self.text("HIGHSCORES", "big", YELLOW, (cx, 120))
        if not highscores:
            self.text("No scores yet", "menu", GREY, (cx, 300))
        for i, entry in enumerate(highscores[:10]):
            line = f"{i + 1:>2}.  {entry['name']:<10}  {entry['score']}"
            self.text(line, "menu", WHITE, (cx, 240 + i * 48))
        self.text(
            "Press ESC or SPACE to return",
            "small",
            GREY,
            (cx, 760),
        )

    def draw_hud(
        self,
        score: int,
        lives: int,
        level: int,
        time_left: float,
        cheats: Optional[list[str]] = None,
    ) -> None:
        pygame.draw.rect(
            self.screen, (15, 15, 40), (0, 0, self.width, 60)
        )
        self.text(f"Score: {score}", "hud", WHITE, (140, 30))
        self.text(f"Lives: {lives}", "hud", WHITE, (380, 30))
        self.text(f"Level: {level}", "hud", WHITE, (600, 30))
        self.text(
            f"Time: {int(time_left)}s", "hud", WHITE, (820, 30)
        )
        if cheats:
            self.text(
                "CHEATS: " + " ".join(cheats),
                "small",
                RED,
                (self.width - 260, 30),
            )

    def draw_pause(self) -> None:
        self._overlay()
        cx = self._cx()
        self.text("PAUSED", "big", YELLOW, (cx, self.height // 2 - 80))
        self.text("[P] Resume", "menu", WHITE, (cx, self.height // 2))
        self.text(
            "[ESC] Main Menu", "menu", WHITE,
            (cx, self.height // 2 + 55),
        )

    def draw_game_over(self, score: int) -> None:
        self._overlay()
        cx = self._cx()
        self.text("GAME OVER", "big", RED, (cx, self.height // 2 - 80))
        self.text(
            f"Final Score: {score}", "menu", WHITE,
            (cx, self.height // 2),
        )

    def draw_victory(self, score: int) -> None:
        self._overlay()
        cx = self._cx()
        self.text("YOU WIN!", "big", YELLOW, (cx, self.height // 2 - 80))
        self.text(
            "All levels cleared!", "menu", CYAN,
            (cx, self.height // 2 - 10),
        )
        self.text(
            f"Final Score: {score}", "menu", WHITE,
            (cx, self.height // 2 + 45),
        )

    def draw_name_entry(self, current: str, score: int) -> None:
        self._overlay()
        cx = self._cx()
        self.text(
            "NEW HIGHSCORE!", "big", YELLOW,
            (cx, self.height // 2 - 120),
        )
        self.text(
            f"Score: {score}", "menu", WHITE,
            (cx, self.height // 2 - 50),
        )
        self.text(
            "Enter your name:", "small", GREY,
            (cx, self.height // 2 + 5),
        )
        shown = current + "_"
        self.text(
            shown, "big", CYAN,
            (cx, self.height // 2 + 60),
        )
        self.text(
            "[ENTER] Save", "small", GREY,
            (cx, self.height // 2 + 130),
        )

    def draw_loading(self, level: int) -> None:
        self.screen.fill(BLACK)
        cx, cy = self._cx(), self.height // 2
        self.text(f"LEVEL {level}", "big", YELLOW, (cx, cy - 40))
        self.text("Generating maze...", "menu", WHITE, (cx, cy + 40))

    def _overlay(self) -> None:
        layer = pygame.Surface((self.width, self.height))
        layer.set_alpha(180)
        layer.fill(BLACK)
        self.screen.blit(layer, (0, 0))
