from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from .sprite import VisibleSprite, Layers
from .storm import Storm, StormAnim
from .constants import VEC

from random import randint, uniform, choice
from math import cos, sin, pi
from pygame.locals import *
from uuid import uuid4
import pygame
import time

class Swirl(VisibleSprite):
    def __init__(self, scene: Scene, layer: Layers, size: int, density: int = 6, dot_sizes=[1, 2, 2]) -> None:
        super().__init__(scene, layer)
        self.size = size
        self.pos = VEC(0, 0)

        self.image = pygame.Surface((self.size, self.size))
        self.image.fill((255, 255, 255))
        self.dots = []
        for _ in range(density):
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
                choice(dot_sizes) # radius
            ])
        self.visible = True

    def update(self) -> None:
        for dot in self.dots:
            pos = VEC(dot[0](time.time() * dot[4] + dot[3]), dot[1](time.time() * dot[4] + dot[3]))
            pygame.draw.aacircle(self.image, dot[2], pos, dot[5])

    def draw(self) -> None:
        if not self.visible: return
        self.image.fill((2, 2, 2), special_flags=BLEND_ADD)
        self.scene.manager.screen.blit(self.image, self.pos - self.scene.player.camera.offset, special_flags=BLEND_MULT)

class StormSwirl(Swirl):
    instances = {}

    def __init__(self, scene: Scene, layer: Layers, storm: Storm, pos: VEC, size: int, density: int = 6, id: str = None) -> None:
        super().__init__(scene, layer, size, density, range(2, 4))
        self.storm = storm
        self.pos = pos
        self.timer = time.time()
        self.orig_img = self.image.copy()

        if id is None:
            self.id = storm.id
        else:
            self.id = id
        __class__.instances[self.id] = self

    def update(self) -> None:
        if getattr(self, "storm", None) is None: return
        super().update()

        if time.time() - self.timer > 0.1:
            self.timer = time.time()
            for _ in range(2):
                StormAnim(self.scene, self.pos + (self.size / 2,) * 2, self.storm)

        self.image.fill((max(self.storm.alpha * 0.15 - 20, 0),) * 3, special_flags=BLEND_ADD)

        if self.storm.alpha == 255:
            self.kill()

    def draw(self) -> None:
        if getattr(self, "storm", None) is None: return
        super().draw()

    def kill(self) -> None:
        __class__.instances.pop(self.storm.id)
        super().kill()