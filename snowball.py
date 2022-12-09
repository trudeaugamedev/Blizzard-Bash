from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene
    from player import Player

import pygame

from sprite import VisibleSprite, Layers
from constants import VEC, GRAVITY
from ground import Ground

class Snowball(VisibleSprite):
    def __init__(self, scene: Scene, vel: tuple[float, float]) -> None:
        super().__init__(scene, Layers.SNOWBALL)

        self.player: Player = self.scene.player # Type annotation just bcs I need intellisense lol
        self.pos = self.player.pos + self.player.SB_OFFSET
        self.vel = VEC(vel)
        self.acc = VEC(0, 0)

    def update(self) -> None:
        self.acc = VEC(0, GRAVITY)
        self.acc += self.scene.wind

        self.vel += self.acc * self.manager.dt
        self.pos += self.vel * self.manager.dt

        for ground in Ground.instances:
            if ground.rect.collidepoint(self.pos):
                self.kill()
        if self.pos.y > 1000:
            self.kill()

    def draw(self) -> None:
        pygame.draw.circle(self.manager.screen, (255, 255, 255), self.pos - self.player.camera.offset, 5)