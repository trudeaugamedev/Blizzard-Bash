from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager

from pygame.locals import K_RETURN, KEYDOWN
from random import randint, choice
import opensimplex as noise
import time

from .constants import TILE_SIZE, WIDTH, VEC, HEIGHT, FONT
from .snowflake import SnowFlake
from .powerup import Powerup
from .ground import Ground
from .player import Player
from .scene import Scene

class MainGame(Scene):
    def __init__(self, manager: GameManager, previous_scene: Scene) -> None:
        super().__init__(manager, previous_scene)
        while "seed" not in self.client.thread_data:
            time.sleep(0.01)
        noise.seed(self.client.thread_data["seed"])

        for x in range(-42, 43):
            # Horizontal stretch and vertical stretch (essentially)
            y = noise.noise2(x * 0.1, 0) * 200
            Ground(self, (x * TILE_SIZE, y), (TILE_SIZE, 800))
        for x in range(-63, -42):
            y = noise.noise2(x * 0.1, 0) * 200 - 400
            Ground(self, (x * TILE_SIZE, y), (TILE_SIZE, 2000))
        for x in range(43, 64):
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
            for player in self.manager.other_players.values():
                if self.score > player.score:
                    break
            else:
                if self.manager.other_players:
                    self.lost = True
                self.manager.new_scene("EndMenu")
            del self.client.thread_data["eliminate"]

        if KEYDOWN in self.manager.events and self.manager.events[KEYDOWN].key == K_RETURN:
            self.manager.ready = True

    def draw(self) -> None:
        self.manager.screen.fill((169, 192, 203))
        super().draw()
        self.manager.screen.blit(FONT[56].render(f"Score: {self.score}", True, (0, 0, 0)), (10, 10))
        if "ready" not in self.client.thread_data:
            text = FONT[70].render("Waiting for Players to get Ready...", True, (0, 0, 0))
            self.manager.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            if not self.manager.ready:
                text = FONT[40].render("Press Enter when you are Ready!", True, (0, 0, 0))
            else:
                text = FONT[40].render("You are ready!", True, (0, 0, 0))
            self.manager.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + 50))