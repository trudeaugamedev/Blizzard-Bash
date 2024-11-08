from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .scene import Scene

from .sprite import VisibleSprite, Sprite, Layers
from .constants import VEC, PIXEL_SIZE
from . import assets

from random import randint, uniform
from math import sqrt
import pygame

MAX_R = 80

class Storm(VisibleSprite):
    def __init__(self, scene: Scene, pos: VEC, size: VEC) -> None:
        super().__init__(scene, Layers.STORM)
        self.pos = pos
        self.size = size
        self.blobs = []
        self.image = pygame.Surface(size + (MAX_R * 2, MAX_R * 2))
        self.image.fill((255, 255, 255))
        for _ in range(int(sqrt(size.x * size.y) / 6)):
            offset = VEC(0, -randint(0, int(size.x / 2))).rotate(randint(-90, 90))
            blob = StormBlob(self.scene, self, offset, randint(40, MAX_R))
            self.blobs.append(blob)
            blob.draw()
        self.image.blit(pygame.transform.scale(assets.storm_gradient, self.image.size), (0, 0), special_flags=pygame.BLEND_ADD)

        self.image = pygame.transform.scale(self.image, VEC(self.image.size) // PIXEL_SIZE)
        self.image = pygame.transform.scale(self.image, VEC(self.image.size) * PIXEL_SIZE)

        self.speed_factor = uniform(0.5, 1.5)

    def update(self) -> None:
        self.pos.x += self.scene.wind_vel.x * self.speed_factor * 0.05 * self.manager.dt

    def draw(self) -> None:
        self.scene.manager.screen.blit(self.image, self.pos - (self.size.x / 2, self.size.y) - self.scene.player.camera.offset, special_flags=pygame.BLEND_MULT)

class StormBlob:
    def __init__(self, scene: Scene, storm: Storm, offset: VEC, radius: int) -> None:
        self.scene = scene
        self.storm = storm
        self.offset = offset
        self.radius = radius

    def draw(self) -> None:
        pygame.draw.circle(self.storm.image, (39, 43, 49), self.offset + (self.storm.image.size[0] / 2, self.storm.image.size[1]) - (0, MAX_R), self.radius)
