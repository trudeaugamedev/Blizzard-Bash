from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

import pygame
import time

from .constants import VEC, GRAVITY, PIXEL_SIZE
from .sprite import VisibleSprite, Layers
from .ground import Ground

class Powerup(VisibleSprite):
    def __init__(self, scene: Scene, pos: tuple[int, int]) -> None:
        super().__init__(scene, Layers.POWERUP)
        if self.scene.powerup:
            try:
                self.scene.powerup.kill()
            except ValueError:
                pass
            self.scene.powerup = None
        self.pos = VEC(pos)
        self.vel = VEC(0, 0)
        self.radius = 14

    def update(self) -> None:
        self.vel.y += GRAVITY * self.manager.dt
        self.vel += self.scene.wind_vel * 2 * self.manager.dt
        self.vel *= 0.99
        self.pos += self.vel * self.manager.dt

        ground_y = Ground.height_map[int(self.pos.x // PIXEL_SIZE * PIXEL_SIZE)]
        if self.pos.y > ground_y - self.radius:
            self.pos.y = ground_y - self.radius
            self.vel = VEC(0, 0)

        if self.pos.distance_to(VEC(self.scene.player.real_rect.center)) < 60:
            self.scene.player.powerup = True
            self.scene.player.powerup_time = time.time()
            self.kill()
            return
        for player in self.manager.other_players.values():
            if self.pos.distance_to(VEC(player.real_rect.center)) < 60:
                self.kill()
                return

    def draw(self) -> None:
        pygame.draw.circle(self.manager.screen, (255, 0, 0), self.pos - self.scene.player.camera.offset, self.radius)

    def kill(self) -> None:
        self.scene.powerup = None
        super().kill()