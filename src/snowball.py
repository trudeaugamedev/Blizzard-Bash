from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene
    from player import Player

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

        self.landed = False

    def update(self) -> None:
        self.image = self.type[self.frame]

        if self.landed:
            if time.time() - self.frame_time > 0.1:
                self.frame_time = time.time()
                self.frame += 1
                if self.frame == self.type.length:
                    super().kill()
            return

        self.acc = VEC(0, GRAVITY)
        self.acc += self.scene.wind

        self.vel += self.acc * self.manager.dt
        self.pos += self.vel * self.manager.dt
        self.rect = self.image.get_rect(center=self.pos)

        for ground in Ground.instances:
            if ground.rect.collidepoint(self.pos):
                self.kill()
                return

        if self.pos.y > 1000:
            self.kill()

    def draw(self) -> None:
        # pygame.draw.circle(self.manager.screen, (255, 255, 255), self.pos - self.player.camera.offset, 5)
        self.manager.screen.blit(self.image, VEC(self.rect.topleft) - self.player.camera.offset)

    def kill(self) -> None:
        self.scene.player.snowball = None
        self.landed = True