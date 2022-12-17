from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene
    from player import Player

from random import randint, choice
import pygame
import time

from .sprite import VisibleSprite, Layers
from .constants import VEC, GRAVITY
from .ground import Ground
from . import assets

class Snowball(VisibleSprite):
    def __init__(self, scene: Scene, vel: tuple[float, float]) -> None:
        super().__init__(scene, Layers.SNOWBALL)

        self.player: Player = self.scene.player # Type annotation just bcs I need intellisense lol
        self.pos = self.player.pos + self.player.SB_OFFSET
        self.vel = VEC(vel)
        self.acc = VEC(0, 0)
        self.size = VEC(0, 0)
        self.frame = 0
        self.frame_time = time.time()
        self.type = assets.snowball_large
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
                    self.scene.player.snowball = None
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

        for ground in Ground.instances:
            if ground.rect.colliderect(self.real_rect):
                self.kill()
                return

        for player in self.manager.other_players.values():
            if player.rect.colliderect(self.real_rect):
                self.kill()
                self.scene.score += 1
                return

        if self.pos.y > 1000:
            self.kill()

    def draw(self) -> None:
        # pygame.draw.circle(self.manager.screen, (255, 255, 255), self.pos - self.player.camera.offset, 5)
        self.manager.screen.blit(self.image, VEC(self.rect.topleft) - self.player.camera.offset)

    def kill(self) -> None:
        self.landed = True