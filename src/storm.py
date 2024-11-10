from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .scene import Scene

from .sprite import VisibleSprite, Sprite, Layers
from .constants import VEC, PIXEL_SIZE
from .utils import inttup
from . import assets

from random import randint, uniform, choice
import pytweening as tween
from uuid import uuid4
from math import sqrt
import pygame
import time

MIN_R = 15
MAX_R = 28

class Storm(VisibleSprite):
    edge_imgs = [pygame.Surface((32, 32)), pygame.Surface((48, 48)), pygame.Surface((64, 64)), pygame.Surface((80, 80))]
    for img in edge_imgs:
        pygame.draw.circle(img, (2, 2, 2), (img.width // 2, img.height // 2), img.width // 2)

    def __init__(self, scene: Scene, id: str, pos: VEC, size: VEC) -> None:
        super().__init__(scene, Layers.STORM)
        self.id = id
        self.pos = pos
        self.vel = VEC(0, 0)
        self.size = size / PIXEL_SIZE
        self.blobs = []
        self.image = pygame.Surface(self.size + (MAX_R * 2, MAX_R * 2), pygame.SRCALPHA)
        for _ in range(int(sqrt(self.size.x * self.size.y) / 2)):
            # semi-elliptical distribution
            offset = VEC(0, -self.size.y).rotate(randint(-90, 90))
            offset.x *= self.size.x / 2 / self.size.y
            offset.scale_to_length(randint(0, int(offset.length())))
            offset += (self.image.width // 2, self.image.height - MAX_R)
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
        self.center_pos = self.pos + VEC(self.image.size) / 2
        self.lifetime = 13
        self.lifetime_timer = time.time()
        self.disappearing = False

        self.snowball_timer = time.time()

        # for data transmission to other clients
        self.offsets = [inttup(blob.offset) for blob in self.blobs]
        self.radii = [blob.radius for blob in self.blobs]
        self.scene.player.storms.append(self)

    def update(self) -> None:
        self.center_pos = self.pos + VEC(self.image.size) / 2

        if self.manager.other_players:
            nearest_player = min(self.manager.other_players.values(), key=lambda p: self.center_pos.distance_to(p.pos))
            self.vel.x = (nearest_player.pos.x - self.center_pos.x) * 1.0

        self.pos += self.vel * self.manager.dt

        self.alpha += 80 * self.manager.dt
        if self.alpha > 255:
            self.alpha = 255
        self.image.set_alpha(self.alpha)

        if self.alpha >= 255:
            if time.time() - self.snowball_timer > 0.18:
                offset = VEC(choice(self.offsets)) * PIXEL_SIZE
                self.scene.player.spawn_snowball(randint(0, 1), self.pos + offset, VEC(0, 0), follow=False)
                self.snowball_timer = time.time()

        if time.time() - self.lifetime_timer > self.lifetime:
            self.disappearing = True

        if self.disappearing:
            self.alpha -= 600 * self.manager.dt
            if self.alpha <= 0:
                self.kill()

    def draw(self) -> None:
        self.scene.manager.screen.blit(self.image, self.pos - self.scene.player.camera.offset)

    def kill(self) -> None:
        self.scene.player.storms.remove(self)
        self.client.irreg_data.put({"storm_id": self.id, "player_id": self.client.id})
        super().kill()

class StormAnim(VisibleSprite):
    def __init__(self, scene: Scene, pos: VEC, storm: Storm) -> None:
        super().__init__(scene, Layers.STORM_ANIM)
        self.start_pos = pos.copy()
        self.pos = pos.copy()
        blob = choice(storm.blobs)
        radius = blob.radius * PIXEL_SIZE
        self.target_offset = blob.offset * PIXEL_SIZE
        self.target_pos = storm.pos + self.target_offset
        self.radius = radius
        self.scale = 0
        self.storm = storm
        self.orig_image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.orig_image, (138, 155, 178), (radius, radius), radius)
        self.orig_image.set_alpha(50)
        self.alpha_target = self.storm.alpha * 0.7
        self.linear_progress = 0
        self.progress = 0

    def update(self) -> None:
        self.linear_progress += 1.0 * self.manager.dt
        self.progress = tween.easeOutCubic(self.linear_progress)

        if self.linear_progress < 1:
            self.alpha_target = self.storm.alpha * 0.7
            self.alpha = self.progress * (self.alpha_target - 50) + 50
        else:
            self.alpha -= 270 * self.manager.dt
        self.orig_image.set_alpha(self.alpha)

        if self.alpha <= 0:
            self.kill()

        self.target_pos = self.storm.pos + self.target_offset
        self.pos = self.progress * (self.target_pos - self.start_pos) + self.start_pos

        self.scale = min(self.progress, 1)

    def draw(self) -> None:
        image = pygame.transform.scale_by(self.orig_image, self.scale)
        self.scene.manager.screen.blit(image, self.pos - VEC(image.size) // 2 - self.scene.player.camera.offset)

class StormBlob:
    def __init__(self, scene: Scene, storm: Storm, offset: VEC, radius: int) -> None:
        self.scene = scene
        self.storm = storm
        self.offset = offset
        self.radius = radius

    def draw(self) -> None:
        pygame.draw.circle(self.storm.image, (138, 155, 178), self.offset, self.radius)
