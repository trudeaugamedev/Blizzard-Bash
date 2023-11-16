from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager

from .constants import WIDTH, HEIGHT
from .button import Button
from .scene import Scene
from . import assets

class StartMenu(Scene):
    def __init__(self, manager: GameManager, previous_scene: Scene) -> None:
        super().__init__(manager, previous_scene)
        self.start_button = Button(
            self, (WIDTH // 2, HEIGHT // 2), (300, 80), "JOIN GAME",
            lambda: self.manager.new_scene("MainGame"), centered=True
        )

    def update(self) -> None:
        super().update()

    def draw(self) -> None:
        self.manager.screen.blit(assets.background, (0, 0))
        super().draw()