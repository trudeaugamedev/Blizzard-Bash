from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager

from player import Player
from scene import Scene

class MainGame(Scene):
    def __init__(self, manager: GameManager, previous_scene: Scene) -> None:
        super().__init__(manager, previous_scene)
        self.player = Player(self)

    def draw(self) -> None:
        self.manager.screen.fill((80, 80, 80))
        super().draw()