from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from pygame.locals import SRCALPHA, BLEND_RGB_SUB
from math import atan2, degrees
from random import uniform
import pygame
import time

from .constants import TILE_SIZE, VEC, PIXEL_SIZE, REAL_TILE_SIZE, WIDTH
from .sprite import VisibleSprite, Layers
from . import assets

class Mist(VisibleSprite):
    def __init__(self, scene: Scene, pos: tuple[int, int]) -> None:
        super().__init__(scene, Layers.BORDER)
        self.pos = VEC(pos)
        self.vel = VEC(0, 0)
        self.resistance = uniform(0.6, 0.8)
        self.image = assets.mist.copy()
        self.start_time = time.time()
        self.opacity = 1
        self.appeared = False
        self.image.set_alpha(self.opacity)

    def update(self) -> None:
        self.vel += self.scene.wind_vel * 1.5 * self.manager.dt
        self.vel *= self.resistance
        self.pos += self.vel * self.manager.dt

        if self.pos.x > self.scene.player.camera.offset.x + 600 + self.image.get_width() // 2 or self.pos.x < self.scene.player.camera.offset.x - 600 - self.image.get_width() // 2:
            self.opacity = 200
            self.appeared = True

        if not self.appeared:
            self.opacity += 100 * self.manager.dt
        if self.opacity > 200 and not self.appeared:
            self.opacity = 200
            self.appeared = True
            self.start_time = time.time()
        if time.time() - self.start_time > 5:
            self.opacity -= 100 * self.manager.dt
        if self.opacity <= 0:
            self.kill()
            return
        self.image.set_alpha(self.opacity)

    def draw(self) -> None:
        self.manager.screen.blit(self.image, self.pos - VEC(self.image.get_size()) // 2 - self.scene.player.camera.offset)

    def kill(self) -> None:
        self.scene.mists.remove(self)
        super().kill()