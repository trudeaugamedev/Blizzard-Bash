from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from pygame.locals import K_a, K_d, K_w, K_SPACE, MOUSEBUTTONUP
import pygame
import time

from .utils import intvec, snap, clamp, clamp_max
from .constants import VEC, SCR_DIM, GRAVITY
from .sprite import VisibleSprite, Layers
from .snowball import Snowball
from .ground import Ground

class OtherPlayer(VisibleSprite):
    def __init__(self, scene: Scene, pos: tuple[int, int]) -> None:
        super().__init__(scene, Layers.PLAYER)
        self.size = VEC(30, 40)
        self.pos = VEC(pos)

    def update(self) -> None:
        ...

    def draw(self) -> None:
        pygame.draw.rect(self.manager.screen, (255, 255, 0), (*(self.pos - self.scene.player.camera.offset), *self.size))