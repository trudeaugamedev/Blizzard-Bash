from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager

from random import randint, choice
from vnoise import Noise
import time

from constants import STEP_WIDTH, WIDTH, VEC, HEIGHT
from snowflake import SnowFlake
from house import House
from ground import Ground
from player import Player
from scene import Scene

noise = Noise()

class MainGame(Scene):
    def __init__(self, manager: GameManager, previous_scene: Scene) -> None:
        super().__init__(manager, previous_scene)
        self.player = Player(self)

        for x in range(-100, 101):
            # Horizontal stretch and vertical stretch (essentially)
            y = noise.noise1(x * 0.05) * 200
            Ground(self, (x * STEP_WIDTH, y), (STEP_WIDTH, 500))
        for _ in range(10):
            ground = choice(Ground.instances)
            House(self, (ground.pos.x, ground.pos.y))

        self.snowflake_time = time.time()
        for _ in range(1000):
            SnowFlake(self, VEC(randint(0 - 1000, WIDTH + 1000), randint(-400, HEIGHT)) + self.player.camera.offset)

        self.wind = VEC(choice([randint(-600, -200), randint(200, 600)]), 0)
        self.wind_time = time.time()
        self.wind_interval = randint(5, 10)

    def update(self) -> None:
        super().update()

        if time.time() - self.wind_time > self.wind_interval:
            self.wind = VEC(choice([randint(-600, -200), randint(200, 600)]), 0)
            self.wind_time = time.time()
            self.wind_interval = randint(3, 6)

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