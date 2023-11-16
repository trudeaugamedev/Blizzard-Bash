from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager

from .sprite import SpriteManager

class Scene:
    def __init__(self, manager: GameManager, previous_scene: Scene) -> None:
        self.manager = manager
        self.client = manager.client
        self.previous_scene = previous_scene
        self.sprite_manager = SpriteManager(self)
        self.running = True

    def setup(self) -> None:
        pass

    def update(self) -> None:
        self.sprite_manager.update()

    def draw(self) -> None:
        self.sprite_manager.draw()