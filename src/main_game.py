from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager

import opensimplex as noise
from random import randint, choice
import time

from .constants import TILE_SIZE, WIDTH, VEC, HEIGHT, FONT
from .snowflake import SnowFlake
from .house import House
from .ground import Ground
from .player import Player
from .scene import Scene

class MainGame(Scene):
    def __init__(self, manager: GameManager, previous_scene: Scene) -> None:
        super().__init__(manager, previous_scene)
        while "seed" not in self.client.thread_data:
            time.sleep(0.01)
        noise.seed(self.client.thread_data["seed"])

        for x in range(-100, 101):
            # Horizontal stretch and vertical stretch (essentially)
            y = noise.noise2(x * 0.1, 0) * 200
            Ground(self, (x * TILE_SIZE, y), (TILE_SIZE, 800))
        for ground in Ground.instances.values():
            ground.generate_image() # Create a images only after all tiles have been created

        self.player = Player(self)

        for _ in range(10):
            ground = choice(list(Ground.instances.values()))
            House(self, (ground.pos.x, ground.pos.y))

        self.snowflake_time = time.time()
        for _ in range(1000):
            SnowFlake(self, VEC(randint(0 - 1000, WIDTH + 1000), randint(-400, HEIGHT)) + self.player.camera.offset)

        self.wind_vel = VEC((self.client.thread_data["wind"] if "wind" in self.client.thread_data else 0), 0)

        self.score = 0

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

    def draw(self) -> None:
        self.manager.screen.fill((169, 192, 203))
        super().draw()
        self.manager.screen.blit(FONT[56].render(f"Score: {self.score}", True, (0, 0, 0)), (10, 10))