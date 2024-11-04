from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene
    from player import Player

from pygame.locals import BLEND_RGB_SUB
from random import randint, choice
import pygame
import time

from .constants import VEC, GRAVITY, PIXEL_SIZE
from .sprite import VisibleSprite, Layers
from .utils import shadow, sign
from .powerup import Powerup
from .ground import Ground1
from . import assets

class Snowball(VisibleSprite):
    def __init__(self, scene: Scene, vel: tuple[float, float], sb_type) -> None:
        super().__init__(scene, Layers.SNOWBALL)

        self.player: Player = self.scene.player # Type annotation just bcs I need intellisense lol
        self.pos = self.player.rect.topleft + self.player.SB_OFFSET
        self.vel = VEC(vel)
        self.acc = VEC(0, 0)
        self.size = VEC(0, 0)
        self.frame = 0
        self.frame_time = time.time()
        self.type = sb_type
        self.score = 1 if self.type == assets.snowball_small else 4
        self.image = self.type[self.frame]
        self.rect = self.image.get_rect(center=self.pos)
        self.real_rect = pygame.Rect(0, 0, *(10, 10) if self.type == assets.snowball_large else (7, 7))
        self.real_rect.center = self.rect.center
        self.landed = False
        self.rotation = 0
        self.rot_speed = choice([randint(-400, -100), randint(100, 400)])

    def update(self) -> None:
        self.image = self.type[self.frame]
        self.rect = self.image.get_rect(center=self.pos)

        if self.landed:
            if time.time() - self.frame_time > 0.08:
                self.frame_time = time.time()
                self.frame += 1
                if self.frame == self.type.length:
                    self.scene.player.snowballs.remove(self)
                    super().kill()
            return

        self.rotation += self.rot_speed * self.manager.dt
        self.image = pygame.transform.rotate(self.type[self.frame], self.rotation)

        self.acc = VEC(0, GRAVITY)
        self.acc += self.scene.wind_vel

        self.vel += self.acc * self.manager.dt
        self.pos += self.vel * self.manager.dt
        self.rect = self.image.get_rect(center=self.pos)
        self.real_rect.center = self.rect.center

        try:
            ground_y = Ground1.height_map[int(self.rect.centerx // PIXEL_SIZE * PIXEL_SIZE)]
        except KeyError:
            self.kill()
            return
        if self.pos.y > ground_y:
            self.kill()
            return

        for player in self.manager.other_players.values():
            if player.real_rect.colliderect(self.real_rect):
                sound = choice(assets.hit_sounds)
                sound.set_volume(self.score ** 2 * 0.2)
                sound.play()
                self.scene.hit = True
                self.scene.hit_pos = self.pos
                self.kill()
                if not self.scene.waiting and not self.scene.eliminated:
                    self.scene.score += self.score * (2 if self.player.powerup == "strength" else 1)
                    self.client.queue_data("score", self.scene.score)
                hit_strength = self.score * sign(self.vel.x) * (40 if self.player.powerup == "strength" else 1)
                self.client.irreg_data.put({
                    "hit": hit_strength,
                    "hit_size": 1 if self.type == assets.snowball_small else 2,
                    "hit_powerup": self.player.powerup,
                    "id": player.id
                })
                return

        for powerup in Powerup.instances.values():
            if powerup.rect.colliderect(self.real_rect):
                self.player.powerup = powerup.type
                self.player.powerup_time = time.time()
                self.client.irreg_data.put({"id": powerup.id, "powerup": 1}) # powerup key to uniquify the message

        if self.pos.y > 1000:
            self.kill()

    def draw(self) -> None:
        self.manager.screen.blit(shadow(self.image), VEC(self.rect.topleft) - self.scene.player.camera.offset + (3, 3), special_flags=BLEND_RGB_SUB)
        if self.scene.eliminated:
            self.image.set_alpha(80)
        self.manager.screen.blit(self.image, VEC(self.rect.topleft) - self.player.camera.offset)
        self.image.set_alpha(255)

    def kill(self) -> None:
        self.landed = True