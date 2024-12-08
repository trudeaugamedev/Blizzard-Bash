from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from .sprite import VisibleSprite, Layers
# from .storm import Storm, StormAnim
from .constants import VEC

import pytweening as tween
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
        self.scale = 1

    def update(self) -> None:
        for dot in self.dots:
            pos = VEC(dot[0](time.time() * dot[4] + dot[3]), dot[1](time.time() * dot[4] + dot[3]))
            pygame.draw.aacircle(self.image, dot[2], pos, dot[5])

    def draw(self) -> None:
        if not self.visible: return
        self.image.fill((2, 2, 2), special_flags=BLEND_ADD)
        img = pygame.transform.scale_by(self.image, self.scale)
        self.scene.manager.screen.blit(img, self.pos + (self.size // 2,) * 2 - VEC(img.size) // 2 - self.scene.player.camera.offset, special_flags=BLEND_MULT)

class VortexSwirl(Swirl):
    instances = {}

    def __init__(self, scene: Scene, layer: Layers, pos: VEC, size: int, density: int = 6, id: str = None, suck: bool = False) -> None:
        super().__init__(scene, layer, size, density, range(2, 4))
        # self.storm = storm
        self.pos = pos
        self.timer = time.time()
        self.startTime = time.time()
        self.maxTime = 15
        self.orig_img = self.image.copy()
        self.suck = suck
        self.scale = 0

        # if id is None:
        #     self.id = storm.id
        # else:
        #     self.id = id
        self.id = id
        __class__.instances[self.id] = self

    def update(self) -> None:
        # if getattr(self, "storm", None) is None: return
        super().update()

        self.scale += 3.5 * self.manager.dt
        if self.scale > 1:
            self.scale = 1

        if time.time() - self.timer > 0.1:
            self.timer = time.time()
            for _ in range(2):
                VortexAnim(self.scene, self.pos + (self.scale / 2,) * 2)

            # # funny vortex (i just want to see more snowballs)
            # self.scene.player.spawn_snowball(0, self.pos + (self.size / 2, 0), (0, 0))

        # sucking is on the thrower's side?????
        if self.suck and not self.scene.eliminated:
            if (dist := self.scene.player.pos.distance_to(self.pos + (self.scale / 2,) * 2)) < 250:
                vel = (1 - dist / 250) * (self.pos + (self.scale / 2,) * 2 - self.scene.player.pos).normalize() * 50
                vel.y *= 0.3
                self.scene.player.vel += vel
        for snowball in self.scene.player.snowballs.values():
            if (dist := snowball.pos.distance_to(self.pos + (self.scale / 2,) * 2)) < 250 and dist > 0:
                snowball.vel *= ((dist + 10) / 260) ** self.manager.dt # more friction the closer to center the snowball gets
                snowball.vel += (1 - dist / 250) * (self.pos + (self.scale / 2, self.scale / 2) - snowball.pos).normalize() * 150 # normal accel (toward center)
                snowball.vel += (1.1 - dist / 250) * (self.pos + (self.scale / 2, self.scale / 2) - snowball.pos).normalize().rotate(-90) * 10 # tangent accel (perp. to normal)
                snowball.follow = False # don't mess with people's camera if snowball gets stuck

        self.image.fill((0, 0, 0), special_flags=BLEND_ADD)

        if time.time() - self.startTime > self.maxTime:
            self.kill()

    def draw(self) -> None:
        super().draw()

    def kill(self) -> None:
        try:
            __class__.instances.pop(self.id)
        except KeyError:
            pass
        super().kill()

class VortexAnim(VisibleSprite):
    def __init__(self, scene: Scene, pos: VEC) -> None:
        super().__init__(scene, Layers.STORM_ANIM)
        self.start_pos = pos.copy()
        self.pos = pos.copy()
        # blob = choice(storm.blobs)
        # radius = blob.radius * PIXEL_SIZE
        radius = 0
        # self.target_offset = blob.offset * PIXEL_SIZE
        # self.target_pos = storm.pos + self.target_offset
        self.radius = radius
        self.scale = 0
        # self.storm = storm
        self.orig_image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.orig_image, (138, 155, 178), (radius, radius), radius)
        self.orig_image.set_alpha(50)
        # self.alpha_target = self.storm.alpha * 0.7
        self.alpha_target = 255 * 0.7
        self.linear_progress = 0
        self.progress = 0

    def update(self) -> None:
        self.linear_progress += 1.0 * self.manager.dt
        self.progress = tween.easeOutCubic(self.linear_progress)

        if self.linear_progress < 1:
            # self.alpha_target = self.storm.alpha * 0.7
            self.alpha = self.progress * (self.alpha_target - 50) + 50
        else:
            self.alpha -= 270 * self.manager.dt
        self.orig_image.set_alpha(self.alpha)

        if self.alpha <= 0:
            self.kill()

        # self.target_pos = self.storm.pos + self.target_offset
        # self.pos = self.progress * (self.target_pos - self.start_pos) + self.start_pos

        self.scale = min(self.progress, 1)

    def draw(self) -> None:
        image = pygame.transform.scale_by(self.orig_image, self.scale)
        self.scene.manager.screen.blit(image, self.pos - VEC(image.size) // 2 - self.scene.player.camera.offset)