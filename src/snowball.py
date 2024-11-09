from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene
    from player import Player

from pygame.locals import BLEND_RGB_SUB
from random import randint, choice, uniform
import pygame
import time

from .constants import VEC, GRAVITY, PIXEL_SIZE
from .sprite import VisibleSprite, Layers
from .storm import Storm
from .utils import shadow, sign
from .powerup import Powerup
from .ground import Ground1
from .swirl import Swirl
from . import assets

class Snowball(VisibleSprite):
    def __init__(self, scene: Scene, vel: tuple[float, float], sb_type: int) -> None:
        super().__init__(scene, Layers.SNOWBALL)

        self.player: Player = self.scene.player # Type annotation just bcs I need intellisense lol
        self.pos = self.player.rect.topleft + self.player.SB_OFFSET
        self.vel = VEC(vel)
        self.acc = VEC(0, 0)
        self.size = VEC(0, 0)
        self.frame = 0
        self.frame_time = time.time()
        self.type = sb_type
        self.frames = [assets.snowball_small, assets.snowball_large, assets.snowball_large][sb_type]
        self.score = 1 if self.frames == assets.snowball_small else 4
        self.image = self.frames[self.frame]
        self.rect = self.image.get_rect(center=self.pos)
        self.real_rect = pygame.Rect(0, 0, *(10, 10) if self.frames == assets.snowball_large else (7, 7))
        self.real_rect.center = self.rect.center
        self.landed = False
        self.rotation = 0
        self.rot_speed = choice([randint(-400, -100), randint(100, 400)])

        if self.type == 2:
            self.swirl = Swirl(self.scene, Layers.SNOWBALL, 64)

    def update(self) -> None:
        self.image = self.frames[self.frame]
        self.rect = self.image.get_rect(center=self.pos)

        if self.landed:
            if time.time() - self.frame_time > 0.08:
                self.frame_time = time.time()
                self.frame += 1
                if self.frame == self.frames.length:
                    self.scene.player.snowballs.remove(self)
                    super().kill()
            return

        self.rotation += self.rot_speed * self.manager.dt
        self.image = pygame.transform.rotate(self.frames[self.frame], self.rotation)

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

        if self.collide():
            return

        for powerup in Powerup.instances.values():
            if powerup.rect.colliderect(self.real_rect) and not powerup.touched:
                if powerup.type == "hailstorm":
                    self.scene.player.add_snowball(2)
                    self.scene.player.dig_iterations += 1
                else:
                    self.player.powerup = powerup.type
                    self.player.powerup_time = time.time()
                self.client.irreg_data.put({"id": powerup.id, "powerup": 1}) # powerup key to uniquify the message
                powerup.touched = True

        if self.type == 2:
            self.swirl.pos = self.pos - VEC(32, 32)

        if self.pos.y > 1000:
            self.kill()

    def collide(self) -> bool:
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
                hit_strength = (2 + self.score + (self.score + 6 if self.player.powerup == "strength" else 0)) * sign(self.vel.x)
                self.client.irreg_data.put({
                    "hit": hit_strength,
                    "hit_size": 1 if self.frames == assets.snowball_small else 2,
                    "hit_powerup": self.player.powerup,
                    "id": player.id
                })
                return True
        return False

    def draw(self) -> None:
        self.manager.screen.blit(shadow(self.image), VEC(self.rect.topleft) - self.scene.player.camera.offset + (3, 3), special_flags=BLEND_RGB_SUB)
        if self.scene.eliminated:
            self.image.set_alpha(80)
        self.manager.screen.blit(self.image, VEC(self.rect.topleft) - self.player.camera.offset)
        self.image.set_alpha(255)

    def kill(self) -> None:
        if self.type == 2:
            self.swirl.kill()
            Storm(self.scene, self.pos - (0, 500) + VEC(randint(-80, 80), randint(-20, 20)), VEC(600 + randint(-50, 50), 250 + randint(-50, 50)))
        self.landed = True

class SelfSnowball(Snowball):
    def collide(self) -> bool:
        if self.scene.player.real_rect.colliderect(self.real_rect):
            sound = choice(assets.hit_sounds)
            sound.set_volume(self.score ** 2 * 0.2)
            sound.play()
            self.kill()
            self.scene.player.vel.x = self.score * choice([-1, 1]) * 100
            if not self.scene.waiting and not self.scene.eliminated:
                self.scene.score -= 1
            return True
        return False
