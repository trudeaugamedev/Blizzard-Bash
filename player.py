from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from pygame.locals import K_LEFT, K_RIGHT, K_UP
import pygame

from utils import intvec, snap, clamp, clamp_max
from constants import VEC, SCR_DIM, GRAVITY
from sprite import VisibleSprite, Layers

class Camera:
    def __init__(self, master: Player):
        self.master = master
        self.manager = self.master.manager
        self.float_offset = self.master.pos - VEC(SCR_DIM) / 2 + self.master.size / 2
        self.offset = intvec(self.float_offset)

    def update(self):
        tick_offset = self.master.pos - self.offset - VEC(SCR_DIM) / 2 + self.master.size / 2
        self.float_offset += tick_offset * 5 * self.manager.dt
        self.offset = intvec(self.float_offset)

class Player(VisibleSprite):
    def __init__(self, scene: Scene) -> None:
        super().__init__(scene, Layers.PLAYER)
        self.size = VEC(30, 60)
        self.pos = VEC(0, 0)
        self.vel = VEC(0, 0)
        self.acc = VEC(0, 0)
        self.speed = 150
        self.on_ground = False

        self.CONST_ACC = 500 # 500 pixels per second squared (physics :P)
        self.MAX_SPEED = 200
        self.JUMP_VEL = -400

        self.camera = Camera(self)

    def update(self) -> None:
        keys = pygame.key.get_pressed()

        self.acc = VEC(0, GRAVITY)
        if keys[K_LEFT]: # Acceleration
            self.acc.x -= self.CONST_ACC
        elif self.vel.x < 0: # Deceleration
            self.acc.x += self.CONST_ACC
        if keys[K_RIGHT]:
            self.acc.x += self.CONST_ACC
        elif self.vel.x > 0:
            self.acc.x -= self.CONST_ACC
        if keys[K_UP] and self.on_ground:
            self.vel.y = self.JUMP_VEL

        self.vel += self.acc * self.manager.dt
        # _ to catch the successful clamp return value
        # Baiscally if it clamped to the left it would be -1, right would be 1, if it didn't clamp (value is in range), it's 0
        self.vel.x, _ = clamp(self.vel.x, -self.MAX_SPEED, self.MAX_SPEED)
        # If the absolute value of x vel is less than the constant acceleration, snap to 0 so that deceleration doesn't overshoot
        self.vel.x = snap(self.vel.x, 0, self.CONST_ACC * self.manager.dt)
        self.pos += self.vel * self.manager.dt

        self.pos.y, self.on_ground = clamp_max(self.pos.y, 100 - self.size.y)

        self.camera.update()

    def draw(self) -> None:
        pygame.draw.rect(self.manager.screen, (255, 0, 0), (*(self.pos - self.camera.offset), *self.size))