from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager

from pygame.locals import K_RETURN, KEYDOWN, BLEND_RGB_ADD
from random import randint, choice
from threading import Thread
import opensimplex as noise
import time

from .constants import TILE_SIZE, WIDTH, VEC, HEIGHT, FONT, TEXT_COLOR
from .snowflake import SnowFlake
from .powerup import Powerup
from .ground import Ground
from .player import Player
from .utils import clamp
from .scene import Scene
from . import assets

class MainGame(Scene):
    def setup(self) -> None:
        if self.previous_scene is not None:
            self.client.socket_thread = Thread(target=self.client.socket.run_forever, daemon=True)
            self.client.socket_thread.start()

        while "seed" not in self.client.thread_data:
            time.sleep(0.01)
        noise.seed(self.client.thread_data["seed"])

        for x in range(-42, 43):
            # Horizontal stretch and vertical stretch (essentially)
            y = noise.noise2(x * 0.1, 0) * 200
            Ground(self, (x * TILE_SIZE, y), (TILE_SIZE, 800))
        Ground(self, (-43 * TILE_SIZE, noise.noise2(-43 * 0.1, 0) * 200 - 250), (TILE_SIZE, 2000))
        Ground(self, (43 * TILE_SIZE, noise.noise2(43 * 0.1, 0) * 200 - 250), (TILE_SIZE, 2000))
        for x in range(-63, -43):
            y = noise.noise2(x * 0.1, 0) * 200 - 400
            Ground(self, (x * TILE_SIZE, y), (TILE_SIZE, 2000))
        for x in range(44, 64):
            y = noise.noise2(x * 0.1, 0) * 200 - 400
            Ground(self, (x * TILE_SIZE, y), (TILE_SIZE, 2000))
        for ground in Ground.instances.values():
            ground.generate_image() # Create a images only after all tiles have been created

        self.player = Player(self, self.client.thread_data["id"])

        self.snowflake_time = time.time()
        for _ in range(1000):
            SnowFlake(self, VEC(randint(0 - 1000, WIDTH + 1000), randint(-400, HEIGHT)) + self.player.camera.offset)

        self.wind_vel = VEC((self.client.thread_data["wind"] if "wind" in self.client.thread_data else 0), 0)

        self.powerup_spawn_time = time.time()
        self.powerup = None

        self.score = 0
        self.lost = False
        self.started = False
        self.hit = False
        self.hit_alpha = 255
        self.hit_pos = None

    def update(self) -> None:
        super().update()

        self.wind_vel = VEC((self.client.thread_data["wind"] if "wind" in self.client.thread_data else 0), 0)

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

        if time.time() - self.powerup_spawn_time > 30:
            self.powerup_spawn_time = time.time()
            self.powerup = Powerup(self, self.player.pos + (randint(-200, 200), -600))

        if "eliminate" in self.client.thread_data:
            if not self.manager.other_players:
                self.manager.new_scene("EndMenu")
            for player in self.manager.other_players.values():
                if self.score > player.score:
                    break
            else:
                self.lost = True
                self.manager.new_scene("EndMenu")
            del self.client.thread_data["eliminate"]

        if KEYDOWN in self.manager.events and self.manager.events[KEYDOWN].key == K_RETURN:
            self.manager.ready = True

    def draw(self) -> None:
        self.manager.screen.blit(assets.background, (0, 0))
        super().draw()

        self.manager.screen.blit(FONT[60].render(f"Score: {self.score}", True, TEXT_COLOR), (20, 0))
        text = FONT[60].render(f"Score: {self.score}", True, TEXT_COLOR)
        text.set_alpha(70)
        self.manager.screen.blit(text, VEC(20, 0) + (3, 3))

        topleft = VEC(WIDTH - assets.player_idle[0].get_width() - 10, 10)
        self.manager.screen.blit(assets.player_idle[0], topleft)
        text = FONT[54].render(f"{len(self.manager.other_players)} x", True, TEXT_COLOR)
        text.set_alpha(70)
        self.manager.screen.blit(text, topleft - (text.get_width() + 20, 5) + (3, 3))
        text = FONT[54].render(f"{len(self.manager.other_players)} x", True, TEXT_COLOR)
        self.manager.screen.blit(text, topleft - (text.get_width() + 20, 5))

        if self.hit:
            self.hit_alpha -= 250 * self.manager.dt
            if self.hit_alpha < 0:
                self.hit_alpha = 255
                self.hit = False
            else:
                pos = VEC(self.hit_pos - self.player.camera.offset)
                text = FONT[32].render("HIT!", True, TEXT_COLOR)
                text.set_alpha(self.hit_alpha)
                pos.x, _ = clamp(pos.x, text.get_width() // 2 + 10, WIDTH - text.get_width() // 2 - 10)
                text_shadow = FONT[32].render("HIT!", True, TEXT_COLOR)
                text_shadow.set_alpha(70)
                self.manager.screen.blit(text_shadow, pos - (text.get_width() // 2, 0) + (3, 3))
                self.manager.screen.blit(text, pos - (text.get_width() // 2, 0))

        if "time" in self.client.thread_data:
            text_str = f"Time Left: {self.client.thread_data['time'][0] // 60}:{'0' if self.client.thread_data['time'][0] % 60 < 10 else ''}{self.client.thread_data['time'][0] % 60}"
            text = FONT[30].render(text_str, True, TEXT_COLOR)
            text.set_alpha(70)
            self.manager.screen.blit(text, VEC(20, 72) + (3, 3))
            text = FONT[30].render(text_str, True, TEXT_COLOR)
            self.manager.screen.blit(text, (20, 72))
            
            text_str = f"Next Elimination: {self.client.thread_data['time'][1] // 60}:{'0' if self.client.thread_data['time'][1] % 60 < 10 else ''}{self.client.thread_data['time'][1] % 60}"
            text = FONT[30].render(text_str, True, TEXT_COLOR)
            text.set_alpha(70)
            self.manager.screen.blit(text, VEC(20, 112) + (3, 3))
            text = FONT[30].render(text_str, True, TEXT_COLOR)
            self.manager.screen.blit(text, (20, 112))

        if "ready" not in self.client.thread_data:
            text = FONT[54].render("Waiting for Players to get Ready...", True, (0, 0, 0))
            self.manager.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2 - 20))
            text = FONT[54].render("Waiting for Players to get Ready...", True, (0, 0, 0))
            text.set_alpha(70)
            self.manager.screen.blit(text, VEC(WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2 - 20) + (3, 3))
            if not self.manager.ready:
                text = FONT[30].render("Press Enter when you are Ready!", True, (0, 0, 0))
                self.manager.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 30))
                text = FONT[30].render("Press Enter when you are Ready!", True, (0, 0, 0))
                text.set_alpha(70)
                self.manager.screen.blit(text, VEC(WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 30) + (3, 3))
            else:
                text = FONT[30].render("You are ready!", True, (0, 0, 0))
                self.manager.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 30))
                text = FONT[30].render("You are ready!", True, (0, 0, 0))
                text.set_alpha(70)
                self.manager.screen.blit(text, VEC(WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 30) + (3, 3))