from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .scene import Scene

from .sprite import VisibleSprite, Sprite, Layers
from .constants import VEC, PIXEL_SIZE
from . import assets

from random import randint, uniform, choice
from math import sqrt
import pygame

MIN_R = 15
MAX_R = 28

class Storm(VisibleSprite):
    edge_imgs = [pygame.Surface((32, 32)), pygame.Surface((48, 48)), pygame.Surface((64, 64)), pygame.Surface((80, 80))]
    for img in edge_imgs:
        pygame.draw.circle(img, (2, 2, 2), (img.width // 2, img.height // 2), img.width // 2)

    def __init__(self, scene: Scene, pos: VEC, size: VEC) -> None:
        super().__init__(scene, Layers.STORM)
        self.pos = pos
        self.size = size / 3
        self.blobs = []
        self.image = pygame.Surface(self.size + (MAX_R * 2, MAX_R * 2), pygame.SRCALPHA)
        for _ in range(int(sqrt(self.size.x * self.size.y) / 2)):
            # semi-eliptical distribution
            offset = VEC(0, -randint(0, int(self.size.y))).rotate(randint(-90, 90))
            offset.x *= self.size.x / 2 / self.size.y
            blob = StormBlob(self.scene, self, offset, randint(MIN_R, MAX_R))
            self.blobs.append(blob)
            blob.draw()
        for pos in pygame.mask.from_surface(self.image).outline(3):
            img = choice(self.edge_imgs)
            self.image.blit(img, VEC(pos) - VEC(img.size) // 2, special_flags=pygame.BLEND_ADD)
        self.image.set_alpha(230)
        self.image = pygame.transform.scale_by(self.image, PIXEL_SIZE)

        self.speed_factor = uniform(0.5, 1.5)

    def update(self) -> None:
        self.pos.x += self.scene.wind_vel.x * self.speed_factor * 0.05 * self.manager.dt

    def draw(self) -> None:
        self.scene.manager.screen.blit(self.image, self.pos - (self.size.x / 2, self.size.y) - self.scene.player.camera.offset)

class StormBlob:
    def __init__(self, scene: Scene, storm: Storm, offset: VEC, radius: int) -> None:
        self.scene = scene
        self.storm = storm
        self.offset = offset
        self.radius = radius

    def draw(self) -> None:
        pygame.draw.circle(self.storm.image, (138, 155, 178), self.offset + (self.storm.image.size[0] / 2, self.storm.image.size[1] - MAX_R), self.radius)
