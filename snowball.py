from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene
    from player import Player

import pygame

from sprite import VisibleSprite, Layers
from constants import VEC, GRAVITY

class Snowball(VisibleSprite):
    def __init__(self, scene: Scene, vel: tuple[float, float]) -> None:
        super().__init__(scene, Layers.SNOWBALL)

        self.player: Player = self.scene.player # Type annotation just bcs I need intellisense lol
        self.pos = self.player.pos + self.player.size // 2 - (0, 10)
        self.vel = VEC(vel)
        self.acc = VEC(0, 0)

    def update(self) -> None:
        self.acc = VEC(0, GRAVITY)

        self.vel += self.acc * self.manager.dt
        self.pos += self.vel * self.manager.dt

        if self.pos.y > 100:
            self.kill()

    def draw(self) -> None:
        pygame.draw.circle(self.manager.screen, (255, 255, 255), self.pos - self.player.camera.offset, 5)