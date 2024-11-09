from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .scene import Scene

from .sprite import VisibleSprite, Sprite, Layers
from .constants import VEC, PIXEL_SIZE
from . import assets

from random import randint, uniform, choice
import pytweening as tween
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
        self.size = size / PIXEL_SIZE
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
        self.image = pygame.transform.scale_by(self.image, PIXEL_SIZE)

        self.size *= PIXEL_SIZE
        self.alpha = 0
        self.image.set_alpha(self.alpha)
        self.speed_factor = uniform(0.5, 1.5)

    def update(self) -> None:
        self.pos.x += self.scene.wind_vel.x * self.speed_factor * 0.05 * self.manager.dt

        self.alpha += 80 * self.manager.dt
        if self.alpha > 255:
            self.alpha = 255
        self.image.set_alpha(self.alpha)

    def draw(self) -> None:
        self.scene.manager.screen.blit(self.image, self.pos - (self.size.x / 2, self.size.y) - self.scene.player.camera.offset)

class StormAnim(VisibleSprite):
    def __init__(self, scene: Scene, pos: VEC, radius: int, storm: Storm) -> None:
        super().__init__(scene, Layers.STORM_ANIM)
        self.start_pos = pos.copy()
        self.pos = pos.copy()
        offset = VEC(0, -randint(0, int(storm.size.y))).rotate(randint(-90, 90))
        offset.x *= storm.size.x / 2 / storm.size.y
        offset *= 0.8
        self.target_pos = storm.pos + offset
        self.radius = radius
        self.storm = storm
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (138, 155, 178), (radius, radius), radius)
        self.image.set_alpha(255)
        self.alpha_target = self.storm.alpha * 0.7
        self.linear_progress = 0
        self.progress = 0

    def update(self) -> None:
        self.linear_progress += 1.0 * self.manager.dt
        self.progress = tween.easeOutExpo(self.linear_progress)

        if self.linear_progress < 1:
            self.alpha_target = self.storm.alpha * 0.7
            self.alpha = self.progress * (self.alpha_target - 255) + 255
        else:
            self.alpha -= 270 * self.manager.dt
        self.image.set_alpha(self.alpha)

        if self.alpha <= 0:
            self.kill()

        self.pos = self.progress * (self.target_pos - self.start_pos) + self.start_pos

    def draw(self) -> None:
        self.scene.manager.screen.blit(self.image, self.pos - VEC(self.radius, self.radius) - self.scene.player.camera.offset)

class StormBlob:
    def __init__(self, scene: Scene, storm: Storm, offset: VEC, radius: int) -> None:
        self.scene = scene
        self.storm = storm
        self.offset = offset
        self.radius = radius

    def draw(self) -> None:
        pygame.draw.circle(self.storm.image, (138, 155, 178), self.offset + (self.storm.image.size[0] / 2, self.storm.image.size[1] - MAX_R), self.radius)
