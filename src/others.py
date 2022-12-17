from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

import pygame

from .sprite import VisibleSprite, Layers
from .constants import VEC
from . import assets

class OtherPlayer(VisibleSprite):
    def __init__(self, scene: Scene, pos: tuple[int, int]) -> None:
        super().__init__(scene, Layers.PLAYER)
        self.size = VEC(45, 60)
        self.pos = VEC(pos)
        self.snowball = None

    def update(self) -> None:
        ...

    def draw(self) -> None:
        pygame.draw.rect(self.manager.screen, (255, 255, 0), (*(self.pos - self.scene.player.camera.offset), *self.size))

class OtherSnowball(VisibleSprite):
    def __init__(self, scene: Scene, pos: tuple[int, int]) -> None:
        super().__init__(scene, Layers.SNOWBALL)
        self.pos = VEC(pos)
        self.frame = 0
        self.type = assets.snowball_large
        self.image = self.type[self.frame]
        self.rect = self.image.get_rect(center=self.pos)

    def update(self) -> None:
        self.image = self.type[self.frame]
        self.rect = self.image.get_rect(center=self.pos)

    def draw(self) -> None:
        self.manager.screen.blit(self.image, VEC(self.rect.topleft) - self.scene.player.camera.offset)