from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager

from player import Player
from scene import Scene
from ground import Ground

class MainGame(Scene):
    def __init__(self, manager: GameManager, previous_scene: Scene) -> None:
        super().__init__(manager, previous_scene)
        self.player = Player(self)
        Ground(self, (-200, 100), (100, 50))
        Ground(self, (-100, 90), (100, 50))
        Ground(self, (0, 80), (100, 50))
        Ground(self, (100, 70), (100, 50))
        Ground(self, (200, 60), (100, 50))
        Ground(self, (300, 50), (100, 50))
        Ground(self, (400, 60), (100, 50))
        Ground(self, (500, 70), (100, 50))
        Ground(self, (600, 60), (100, 50))

    def draw(self) -> None:
        self.manager.screen.fill((80, 80, 80))
        super().draw()