from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager

from pygame.locals import K_RETURN, KEYDOWN
from random import randint, choice, seed
import opensimplex as noise
import pygame
import time

from .constants import TILE_SIZE, WIDTH, VEC, HEIGHT, FONT, TEXT_COLOR
from .ground import Ground1Manager, Ground2Manager, Ground3Manager
from .snowflake import SnowFlake, SnowflakeRenderer
from .vignette import FrostVignette, ElimVignette
from .game_leaderboard import GameLeaderboard
from .sprite import Layers
from .player import Player
from .border import Border
from .utils import clamp
from .scene import Scene
from . import assets

class MainGame(Scene):
    def __init__(self, manager: GameManager, previous_scene: Scene) -> None:
        super().__init__(manager, previous_scene)
        # MainGame object must exist before initialization or sprites might get added to the previous scene (StartMenu)

    def setup(self) -> None:
        self.manager.other_players.clear()

        self.waiting = True
        self.eliminated = False
        self.client.restart()
        self.seed = -1
        while self.seed == -1:
            time.sleep(0.01)
        noise.seed(self.seed)

        seed(self.seed)
        Ground1Manager(self)
        Ground2Manager(self)
        Ground3Manager(self)
        seed()

        self.leaderboard = GameLeaderboard(self)

        Border(self, -1)
        Border(self, 1)

        self.player = Player(self)
        self.frost_vignette = FrostVignette(self)
        self.elim_vignette = ElimVignette(self)

        self.snowflake_time = time.time()
        self.snowflake_renderer1 = SnowflakeRenderer(self, Layers.SNOWFLAKE1)
        self.snowflake_renderer2 = SnowflakeRenderer(self, Layers.SNOWFLAKE2)
        self.snowflake_renderer3 = SnowflakeRenderer(self, Layers.SNOWFLAKE3)
        for _ in range(1000):
            SnowFlake(self, VEC(randint(0 - 1000, WIDTH + 1000), randint(-400, HEIGHT)) + self.player.camera.offset)

        self.wind_vel = VEC(0, 0)
        self.time_left = None
        self.total_time = 0
        self.crosshair = 0

        self.score = 0
        self.lost = False
        self.started = False
        self.hit = False
        self.hit_alpha = 255
        self.hit_pos = None

        self.name = self.previous_scene.input_box.text
        self.client.queue_data("name", self.name)
        self.client.queue_data("colors", [self.player.clothes_hue, self.player.hat_hue, self.player.skin_tone])
        self.game_over = False
        self.score_data = []

    def update(self) -> None:
        super().update()

        if time.time() - self.snowflake_time > 0.05:
            self.snowflake_time = time.time()
            for _ in range(14):
                # choose between above left and right so that we can have snowflakes coming in from the side
                # and also so that when we move to the left or right we don't get empty air with no snowflakes
                pos = choice([
                    VEC(randint(-200, WIDTH + 200), -100), # Above
                    VEC(randint(-600, -20), randint(-100, HEIGHT)), # Left
                    VEC(randint(WIDTH, WIDTH + 600), randint(-100, HEIGHT)) # Right
                ])
                SnowFlake(self, pos + self.player.camera.offset)

        if self.time_left is not None:
            self.total_time = max(self.total_time, self.time_left)
            Border.shrink = (1 - self.time_left / self.total_time) * 1600
            Border.update_x(self.manager.dt)

        if KEYDOWN in self.manager.events and self.manager.events[KEYDOWN].key == K_RETURN:
            self.manager.ready = True

        if self.game_over:
            self.manager.new_scene("EndMenu")

        self.client.queue_data("score", self.score)

    def draw(self) -> None:
        self.manager.screen.blit(assets.background, (0, 0))
        super().draw()

        self.manager.screen.blit(FONT[60].render(f"Score: {self.score}", False, TEXT_COLOR), (20, 0))
        text = FONT[60].render(f"Score: {self.score}", False, TEXT_COLOR)
        text.set_alpha(70)
        self.manager.screen.blit(text, VEC(20, 0) + (3, 3))

        if self.hit:
            self.hit_alpha -= 250 * self.manager.dt
            if self.hit_alpha < 0:
                self.hit_alpha = 255
                self.hit = False
            else:
                pos = VEC(self.hit_pos - self.player.camera.offset)
                text = FONT[32].render("HIT!", False, TEXT_COLOR)
                text.set_alpha(self.hit_alpha)
                pos.x, _ = clamp(pos.x, text.get_width() // 2 + 10, WIDTH - text.get_width() // 2 - 10)
                text_shadow = FONT[32].render("HIT!", False, TEXT_COLOR)
                text_shadow.set_alpha(70)
                self.manager.screen.blit(text_shadow, pos - (text.get_width() // 2, 0) + (3, 3))
                self.manager.screen.blit(text, pos - (text.get_width() // 2, 0))

        if self.time_left is not None:
            text_str = f"Time Left: {max(self.time_left // 60, 0)}:{'0' if self.time_left % 60 < 10 else ''}{self.time_left % 60}"
            text = FONT[30].render(text_str, False, TEXT_COLOR)
            text.set_alpha(70)
            self.manager.screen.blit(text, VEC(20, 72) + (3, 3))
            text = FONT[30].render(text_str, False, TEXT_COLOR)
            self.manager.screen.blit(text, (20, 72))

        if self.elim_vignette.flashing and not self.eliminated:
            text = FONT[20].render("You have the least number of points and may be eliminated soon.", False, (255, 0, 0))
            self.manager.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 50))
        elif self.eliminated:
            text = FONT[32].render("You've been eliminated :(", False, (255, 0, 0))
            self.manager.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 80))

        if self.player.powerup is not None:
            text_str = f"{self.player.powerup} - {int(self.player.powerup_max_time - (time.time() - self.player.powerup_time))} seconds remaining"
            text = FONT[30].render(text_str, False, TEXT_COLOR)
            text.set_alpha(70)
            self.manager.screen.blit(text, VEC(WIDTH // 2 - text.get_width() // 2 + 30, HEIGHT - 100) + (3, 3))
            text = FONT[30].render(text_str, False, TEXT_COLOR)
            self.manager.screen.blit(text, VEC(WIDTH // 2 - text.get_width() // 2 + 30, HEIGHT - 100))
            self.manager.screen.blit(pygame.transform.scale_by(assets.powerup_icons[self.player.powerup], 2), (WIDTH // 2 - text.get_width() // 2 - 34, HEIGHT - 100))

        if self.waiting:
            self.draw_waiting_text()

        if 0 < self.player.dig_iterations < 3 or self.player.powerup == "rapidfire":
            if self.crosshair != 1:
                pygame.mouse.set_cursor((7, 7), assets.crosshair_small)
            self.crosshair = 1
        elif self.player.dig_iterations >= 3:
            if self.crosshair != 2:
                pygame.mouse.set_cursor((7, 7), assets.crosshair_large)
            self.crosshair = 2
        else:
            if self.crosshair != 0:
                pygame.mouse.set_cursor((6, 6), assets.crosshair)
            self.crosshair = 0

    def draw_waiting_text(self) -> None:
        text = FONT[54].render("Waiting for game to start...", False, (0, 0, 0))
        self.manager.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
