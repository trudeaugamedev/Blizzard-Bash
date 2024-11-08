from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from .sprite import VisibleSprite, Layers
from .constants import VEC

from random import randint, uniform, choice
from math import cos, sin, pi
from pygame.locals import *
import pygame
import time

class Swirl(VisibleSprite):
    def __init__(self, scene: Scene, layer: Layers, size: int) -> None:
        super().__init__(scene, layer)
        self.size = size
        self.pos = VEC(0, 0)

        self.image = pygame.Surface((self.size, self.size))
        self.image.fill((255, 255, 255))
        self.dots = []
        for _ in range(6):
            size = self.size / 2
            b = uniform(size / 3, size * 2 / 3)
            rot = uniform(0, 2 * pi)
            self.dots.append([
                # late binding GAHHHHHH
                lambda t, b=b, rot=rot: cos(rot) * ((size - 2) * cos(t)) - sin(rot) * (b * sin(t)) + size,
                lambda t, b=b, rot=rot: sin(rot) * ((size - 2) * cos(t)) + cos(rot) * (b * sin(t)) + size,
                (randint(90, 160),) * 3, # color
                uniform(0, 2 * pi), # phase
                uniform(7, 12), # speed
                choice([1, 2, 2]) # radius
            ])

    def update(self) -> None:
        for dot in self.dots:
            pos = VEC(dot[0](time.time() * dot[4] + dot[3]), dot[1](time.time() * dot[4] + dot[3]))
            pygame.draw.aacircle(self.image, dot[2], pos, dot[5])

    def draw(self) -> None:
        self.image.fill((2, 2, 2), special_flags=BLEND_ADD)
        self.scene.manager.screen.blit(self.image, self.pos - self.scene.player.camera.offset, special_flags=BLEND_MULT)