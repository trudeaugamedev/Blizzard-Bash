from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager

from vnoise import Noise

from constants import STEP_WIDTH
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

    def draw(self) -> None:
        self.manager.screen.fill((80, 80, 80))
        super().draw()