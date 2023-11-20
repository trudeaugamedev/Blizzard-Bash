from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from pygame.locals import SRCALPHA, BLEND_RGB_SUB
from math import atan2, degrees
from random import randint
import pygame

from .constants import TILE_SIZE, VEC, PIXEL_SIZE, REAL_TILE_SIZE, WIDTH
from .sprite import VisibleSprite, Layers
from . import assets

class Border(VisibleSprite):
    def __init__(self, scene: Scene, side: int) -> None:
        super().__init__(scene, Layers.BORDER)
        self.side = side
        self.offset = 0

        self.segment = assets.border
        self.image = pygame.Surface((30, 4000), SRCALPHA)
        for i in range(0, 4000, 30):
            self.image.blit(self.segment, (0, i))
        self.image.set_alpha(70)

        self.pos = VEC(side * 2400 - self.segment.get_height() // 2, -2000)

    def update(self) -> None:
        self.offset += 60 * self.manager.dt
        if self.offset > 30:
            self.offset = 0

    def draw(self) -> None:
        self.manager.screen.blit(self.image, self.pos + (0, self.offset) - self.scene.player.camera.offset)