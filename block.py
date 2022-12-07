from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT
import pygame

from sprite import VisibleSprite, Layers
from constants import VEC

# Test blocks for reference, to actually be able to see the player moving
class Block(VisibleSprite):
    def __init__(self, scene: Scene) -> None:
        super().__init__(scene, Layers.PLAYER)
        self.size = VEC(500, 50)
        self.pos = VEC(-200, 100)

    def update(self) -> None:
        ...

    def draw(self) -> None:
        pygame.draw.rect(self.manager.screen, (0, 0, 0), (*(self.pos - self.scene.player.camera.offset), *self.size))