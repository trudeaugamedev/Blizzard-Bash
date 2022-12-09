from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager

from random import randint
from vnoise import Noise
import time

from constants import STEP_WIDTH, WIDTH, VEC
from snowflake import SnowFlake
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
        self.snowflake_time = time.time()

    def update(self) -> None:
        super().update()
        if time.time() - self.snowflake_time > 0.05:
            self.snowflake_time = time.time()
            for _ in range(4):
                SnowFlake(self, VEC(randint(0 - 400, WIDTH + 400), randint(-100, -40)) + self.player.camera.offset)

    def draw(self) -> None:
        self.manager.screen.fill((169, 192, 203))
        super().draw()