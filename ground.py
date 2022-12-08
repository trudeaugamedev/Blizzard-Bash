from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT
import pygame

from sprite import VisibleSprite, Layers
from constants import VEC

# Test blocks for reference, to actually be able to see the player moving
class Ground(VisibleSprite):
    instances = []

    def __init__(self, scene: Scene, pos: tuple[int, int], size: tuple[int, int]) -> None:
        super().__init__(scene, Layers.PLAYER)
        self.__class__.instances.append(self)
        self.size = VEC(size)
        self.pos = VEC(pos)
        self.rect = pygame.Rect(self.pos, self.size)

    def update(self) -> None:
        ...

    def draw(self) -> None:
        pygame.draw.rect(self.manager.screen, (0, 0, 0), (*(self.pos - self.scene.player.camera.offset), *self.size))