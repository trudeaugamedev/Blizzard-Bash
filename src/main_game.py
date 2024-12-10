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
from .sprite import VisibleSprite, Layers
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
        self.hit_neg = False
        self.hit_score = 0
        self.hit_neg_score = 0
        self.hit_alpha = 255
        self.hit_neg_alpha = 255
        self.hit_pos = None
        self.hit_neg_pos = None

        codes = self.previous_scene.input_box.text.split('@')
        self.name = codes[0]
        for i in range(1, len(codes)):
            match codes[i]:
                case "infS":
                    self.player.infinite = True
                    self.player.inf_type = "strength"
                case "infC":
                    self.player.infinite = True
                    self.player.inf_type = "clustershot"
                case "infR":
                    self.player.infinite = True
                    self.player.inf_type = "rapidfire"
                case "infT":
                    self.player.infinite = True
                    self.player.inf_type = "telekinesis"
                case "funT":
                    self.player.funny_tele = True
                case "funC":
                    self.player.funny_cluster = True
                case "funS":
                    self.player.funny_strength = True
                case "funR":
                    self.player.funny_rapid = True
                case "bot$":
                    self.player.can_toggle_bot = True
                case "bot":
                    self.player.aimbot = True
                case "noKB":
                    self.player.no_kb = True
                case c if c.startswith("testLag"):
                    self.player.completely_lag = c[7:]
                case _:
                    self.name += "@"
                    self.name += codes[i]

        self.client.queue_data("name", self.name.lower()) # makes it so that server always receives lowercase names
        self.client.queue_data("colors", [self.player.clothes_hue, self.player.hat_hue, self.player.skin_tone])
        self.game_over = False
        self.score_data = []

    def update(self) -> None:
        super().update()

        if time.time() - self.snowflake_time > 0.05:
            self.snowflake_time = time.time()
            for _ in range(5):
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
            try:
                Border.shrink = (1 - self.time_left / self.total_time) * 1600
            except:
                pass
            Border.update_x(self.manager.dt)

        if KEYDOWN in self.manager.events and self.manager.events[KEYDOWN].key == K_RETURN:
            self.manager.ready = True

        if self.game_over:
            self.manager.new_scene("EndMenu")

        self.client.queue_data("score", self.score)

    def draw(self) -> None:
        self.manager.screen.blit(assets.background, (0, 0))

        super().draw()

        screen_x = int(Border.x - self.player.camera.offset.x)
        for i, x in enumerate(range(screen_x, WIDTH, 15)):
            self.manager.screen.fill((0, min(255, 20 + i * 2), min(255, 20 + i * 2)), (x, 0, 15, HEIGHT), special_flags=pygame.BLEND_SUB)
        screen_x = int(-Border.x + assets.border.width - self.player.camera.offset.x)
        for i, x in enumerate(range(screen_x - 15, -30, -15)):
            self.manager.screen.fill((0, min(255, 20 + i * 2), min(255, 20 + i * 2)), (x, 0, 15, HEIGHT), special_flags=pygame.BLEND_SUB)

        self.manager.screen.blit(FONT[60].render(f"Score: {self.score}", False, TEXT_COLOR), (20, 0))
        text = FONT[60].render(f"Score: {self.score}", False, TEXT_COLOR)
        text.set_alpha(70)
        self.manager.screen.blit(text, VEC(20, 0) + (3, 3))

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

    def draw_waiting_text(self) -> None:
        text = FONT[54].render("Waiting for game to start...", False, (0, 0, 0))
        self.manager.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

    def spawn_hit_text(self, pos: VEC, score: int) -> None:
        HitText(self, pos, score)

class HitText(VisibleSprite):
    hittexts = []

    def __init__(self, scene: MainGame, pos: VEC, score: int) -> None:
        super().__init__(scene, Layers.GUI)
        self.pos = pos
        self.score = score
        self.color = (10, 140, 30) if score > 0 else (180, 20, 40)
        self.alpha = 255
        self.font_size = 32
        self.image = FONT[self.font_size].render(f"{self.score}", False, self.color)
        self.image.set_alpha(self.alpha)

        for text in self.hittexts:
            if text.pos.distance_to(self.pos) < 50 and text.color == self.color:
                text.set_score(text.score + self.score)
                super().kill()
                return

        self.hittexts.append(self)

    def update(self) -> None:
        self.alpha -= 100 * self.scene.manager.dt
        if self.alpha < 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)

    def set_score(self, score: int) -> None:
        self.score = score
        self.font_size += int(min(abs(score), 5))
        if self.font_size > 128:
            self.font_size = 128
        self.image = FONT[self.font_size].render(f"{self.score}", False, self.color)

    def draw(self) -> None:
        pos = self.pos - VEC(self.image.size) // 2 - self.scene.player.camera.offset
        pos = clamp(pos, VEC(40, 40), VEC(WIDTH - 40, HEIGHT - 40))
        self.scene.manager.screen.blit(self.image, pos)

    def kill(self) -> None:
        self.hittexts.remove(self)
        super().kill()
