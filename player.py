from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT
import pygame

from sprite import VisibleSprite, Layers
from constants import VEC

class Player(VisibleSprite):
    def __init__(self, scene: Scene) -> None:
        super().__init__(scene, Layers.PLAYER)
        self.pos = VEC(0, 0)
        self.vel = VEC(0, 0)
        self.speed = 150

    def update(self) -> None:
        keys = pygame.key.get_pressed()
        self.vel = VEC(0, 0)
        if keys[K_LEFT]:
            self.vel.x -= self.speed
        if keys[K_RIGHT]:
            self.vel.x += self.speed
        if keys[K_UP]:
            self.vel.y -= self.speed
        if keys[K_DOWN]:
            self.vel.y += self.speed
        self.pos += self.vel * self.manager.dt

    def draw(self) -> None:
        pygame.draw.rect(self.manager.screen, (255, 0, 0), (*self.pos, 50, 50))