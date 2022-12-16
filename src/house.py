from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from random import randint
import pygame

from .sprite import VisibleSprite, Layers
from .constants import VEC

class House(VisibleSprite):
    instances = []

    def __init__(self, scene: Scene, pos: tuple[int, int]) -> None:
        super().__init__(scene, Layers.HOUSE)
        self.__class__.instances.append(self)
        self.size = VEC(randint(100, 250), 500)
        self.pos = VEC(pos) - (0, self.size.x * 0.7)
        self.rect = pygame.Rect(self.pos, self.size)

    def update(self) -> None:
        ...

    def draw(self) -> None:
        pygame.draw.rect(self.manager.screen, (0, 255, 0), (*(self.pos - self.scene.player.camera.offset), *self.size))
        pygame.draw.rect(self.manager.screen, (0, 0, 255), (*(self.pos - self.scene.player.camera.offset), *self.size), 6)