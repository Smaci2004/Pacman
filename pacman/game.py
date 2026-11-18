from typing import Any

import pygame

from maze.utils import corner_cells
from entities.ghost import Ghost, make_ghosts, EATEN, FRIGHTENED
from entities.pacman import Pacman
from entities.pellets import PelletManager
from services.highscore import HighscoreManager
from maze.loader import MazeError, MazeLoader
from maze.renderer import MazeRenderer
from screens import UI


MENU = "menu"
INSTRUCTIONS = "instructions"
HIGHSCORES = "highscores"
PLAYING = "playing"
PAUSED = "paused"
NAME_ENTRY = "name_entry"
GAME_OVER = "game_over"
VICTORY = "victory"

FRIGHTENED_SECONDS = 7.0
GHOST_RESPAWN_SECONDS = 6.0
END_SCREEN_SECONDS = 3.0

SCATTER_SECONDS = 5.0
CHASE_SECONDS = 20.0

LEVEL_SCREEN_MS = 1500


class Game:

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.ui = UI()
        self.clock = pygame.time.Clock()
        self.highscores = HighscoreManager(config["highscore_filename"])
        self.loader = MazeLoader(
            config["width"], config["height"], config["seed"]
        )
        self.renderer = MazeRenderer()
        self.state = MENU
        self.running = True
        self.maze_error = False

        self.score = 0
        self.lives = config["lives"]
        self.level_index = 0
        self.time_left = 0.0
        self.frightened_timer = 0.0
        self.scatter_timer = SCATTER_SECONDS
        self.scatter_mode = True
        self.name_buffer = ""
        self.end_timer = 0.0
        self.maze: list[list[int]] = []
        self.pacman: Pacman
        self.ghosts: list[Ghost] = []
        self.pellets: PelletManager

        self.cheat_invincible = False
        self.cheat_freeze = False

    def start_new_game(self) -> bool:
        self.score = 0
        self.lives = self.config["lives"]
        self.level_index = 0
        self.cheat_invincible = False
        self.cheat_freeze = False
        return self.load_level()

    def load_level(self) -> bool:
        try:
            self.maze = self.loader.generate(self.level_index)
        except MazeError as exc:
            print(f"[game] {exc}")
            return False

        tile = self.renderer.fit_tile_size(
            self.maze, self.ui.width, self.ui.height
        )
        self.renderer.tile_size = tile
        self.renderer.wall_thickness = max(2, tile // 12)
        self.pacman = Pacman(self.maze, tile)
        corners = corner_cells(self.maze)
        self.ghosts = make_ghosts(self.maze, corners, tile)
        self.pellets = PelletManager(
            self.maze,
            self.config["pacgum"],
            self.config["points_per_pacgum"],
            self.config["points_per_super_pacgum"],
            tile,
            seed=self.config["seed"] + self.level_index,
        )
        self.time_left = float(self.config["level_max_time"])
        self.frightened_timer = 0.0
        self.scatter_timer = SCATTER_SECONDS
        self.scatter_mode = True
        return True

    def respawn_player(self) -> None:
        self.pacman.reset(self.maze)
        for ghost in self.ghosts:
            ghost.reset(self.maze)
        self.frightened_timer = 0.0

    def run(self) -> None:
        try:
            while self.running:
                dt = self.clock.tick(60) / 1000.0
                self.handle_events()
                self.update(dt)
                self.draw()
                pygame.display.flip()
        finally:
            pygame.quit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type != pygame.KEYDOWN:
                continue
            self._handle_key(event)

    def _handle_key(self, event: pygame.event.Event) -> None:
        key = event.key

        if self.state == MENU:
            self._key_menu(key)
        elif self.state in (INSTRUCTIONS, HIGHSCORES):
            if key in (pygame.K_ESCAPE, pygame.K_SPACE):
                self.state = MENU
        elif self.state == PLAYING:
            self._key_playing(event)
        elif self.state == PAUSED:
            self._key_paused(key)
        elif self.state == NAME_ENTRY:
            self._key_name_entry(event)
        elif self.state in (GAME_OVER, VICTORY):
            pass

    def _key_menu(self, key: int) -> None:
        if key == pygame.K_SPACE:
            if self.start_new_game():
                self.state = PLAYING
            else:
                self.maze_error = True
        elif key == pygame.K_i:
            self.state = INSTRUCTIONS
        elif key == pygame.K_h:
            self.state = HIGHSCORES
        elif key == pygame.K_ESCAPE:
            self.running = False

    def _key_playing(self, event: pygame.event.Event) -> None:
        key = event.key

        if key == pygame.K_p:
            self.state = PAUSED
            return

        if key == pygame.K_ESCAPE:
            self.state = MENU
            return

        if key == pygame.K_c:
            self.cheat_invincible = not self.cheat_invincible
        elif key == pygame.K_f:
            self.cheat_freeze = not self.cheat_freeze
        elif key == pygame.K_n:
            self._advance_level()
        elif key == pygame.K_l:
            self.lives += 1

        self.pacman.handle_event(event)

    def _key_paused(self, key: int) -> None:
        if key == pygame.K_p:
            self.state = PLAYING
        elif key == pygame.K_ESCAPE:
            self.state = MENU

    def _key_name_entry(self, event: pygame.event.Event) -> None:
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.highscores.add(self.name_buffer, self.score)
            self.state = MENU
        elif event.key == pygame.K_BACKSPACE:
            self.name_buffer = self.name_buffer[:-1]
        elif len(self.name_buffer) < 10:
            char = event.unicode
            if char.isalnum() or char == " ":
                self.name_buffer += char

    def update(self, dt: float) -> None:
        if self.state in (GAME_OVER, VICTORY):
            self.end_timer -= dt
            if self.end_timer <= 0:
                self._finish_game()
            return

        if self.state != PLAYING:
            return

        self.time_left -= dt
        if self.time_left <= 0:
            self._lose_life()
            return

        self.pacman.update()
        self._update_frightened(dt)
        self._update_scatter(dt)
        pac_cell = (self.pacman.grid_x, self.pacman.grid_y)
        pac_dir = self.pacman.current_dir

        gained, ate_super = self.pellets.check_collision(pac_cell)

        if gained:
            self.score += gained

        if ate_super:
            self.frightened_timer = FRIGHTENED_SECONDS
            for ghost in self.ghosts:
                ghost.set_frightened(True)

        scatter = self.scatter_mode and self.frightened_timer <= 0

        for ghost in self.ghosts:
            ghost.update(
                pac_cell,
                dt,
                frozen=self.cheat_freeze,
                pac_dir=pac_dir,
                scatter=scatter,
            )

        self._check_ghost_collisions(pac_cell)

        if self.pellets.remaining == 0:
            self._advance_level()

    def _update_frightened(self, dt: float) -> None:
        if self.frightened_timer <= 0:
            return

        self.frightened_timer -= dt

        if self.frightened_timer <= 0:
            for ghost in self.ghosts:
                ghost.set_frightened(False)

    def _update_scatter(self, dt: float) -> None:
        self.scatter_timer -= dt

        if self.scatter_timer > 0:
            return

        self.scatter_mode = not self.scatter_mode
        self.scatter_timer = (
            SCATTER_SECONDS
            if self.scatter_mode
            else CHASE_SECONDS
        )

    def _check_ghost_collisions(
        self,
        pac_cell: tuple[int, int],
    ) -> None:
        threshold = self.renderer.tile_size * 0.6

        for ghost in self.ghosts:
            same_cell = (
                (ghost.grid_x, ghost.grid_y) == pac_cell
            )
            close = (
                abs(ghost.x - self.pacman.x) < threshold
                and abs(ghost.y - self.pacman.y) < threshold
            )

            if not (same_cell or close):
                continue

            if ghost.state == EATEN:
                continue

            if ghost.state == FRIGHTENED:
                self.score += self.config["points_per_ghost"]
                ghost.get_eaten(GHOST_RESPAWN_SECONDS)
            elif not self.cheat_invincible:
                self._lose_life()
                return

    def _lose_life(self) -> None:
        self.lives -= 1

        if self.lives <= 0:
            self._end_run(victory=False)
        else:
            self.respawn_player()

    def _advance_level(self) -> None:
        self.level_index += 1

        if self.level_index >= self.config["levels"]:
            self._end_run(victory=True)
            return

        start = pygame.time.get_ticks()
        self.ui.draw_loading(self.level_index + 1)
        pygame.display.flip()
        pygame.event.pump()

        ok = self.load_level()
        elapsed = pygame.time.get_ticks() - start
        remaining = LEVEL_SCREEN_MS - elapsed

        if remaining > 0:
            pygame.time.delay(remaining)

        if not ok:
            self._end_run(victory=False)

    def _end_run(self, victory: bool) -> None:
        self.state = VICTORY if victory else GAME_OVER
        self.end_timer = END_SCREEN_SECONDS

    def _finish_game(self) -> None:
        if self.highscores.qualifies(self.score):
            self.name_buffer = ""
            self.state = NAME_ENTRY
        else:
            self.state = MENU

    def draw(self) -> None:
        if self.state == MENU:
            self.ui.draw_menu(
                self.highscores.top(),
                self.maze_error,
            )
        elif self.state == INSTRUCTIONS:
            self.ui.draw_instructions()
        elif self.state == HIGHSCORES:
            self.ui.draw_highscores(self.highscores.top())
        elif self.state in (
            PLAYING,
            PAUSED,
            GAME_OVER,
            VICTORY,
            NAME_ENTRY,
        ):
            self._draw_game_frame()

            if self.state == PAUSED:
                self.ui.draw_pause()
            elif self.state == GAME_OVER:
                self.ui.draw_game_over(self.score)
            elif self.state == VICTORY:
                self.ui.draw_victory(self.score)
            elif self.state == NAME_ENTRY:
                self.ui.draw_name_entry(
                    self.name_buffer,
                    self.score,
                )

    def _draw_game_frame(self) -> None:
        self.ui.screen.fill((0, 0, 0))
        ox, oy = self.renderer.get_offsets(
            self.ui.screen,
            self.maze,
        )
        self.renderer.draw(
            self.ui.screen,
            self.maze,
            ox,
            oy,
        )
        self.pellets.draw(self.ui.screen, ox, oy)
        self.pacman.draw(self.ui.screen, ox, oy)

        for ghost in self.ghosts:
            ghost.draw(self.ui.screen, ox, oy)

        cheats = []

        if self.cheat_invincible:
            cheats.append("INV")

        if self.cheat_freeze:
            cheats.append("FRZ")

        self.ui.draw_hud(
            self.score,
            self.lives,
            self.level_index + 1,
            self.time_left,
            cheats,
        )
