from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from pygame.locals import K_a, K_d, K_w, K_SPACE, MOUSEBUTTONUP
import pygame
import time

from .utils import intvec, snap, clamp, snap
from .constants import VEC, SCR_DIM, GRAVITY
from .sprite import VisibleSprite, Layers
from .snowball import Snowball
from .ground import Ground

class Camera:
    def __init__(self, master: VisibleSprite, extra_offset: tuple[int, int], follow: int):
        self.master = master
        self.manager = self.master.manager
        self.extra_offset = VEC(extra_offset)
        self.follow = follow
        self.float_offset = self.master.pos - SCR_DIM // 2 - extra_offset + self.master.size / 2
        self.offset = intvec(self.float_offset)

    def update(self):
        tick_offset = self.master.pos - self.offset - SCR_DIM // 2 - self.extra_offset + self.master.size / 2
        tick_offset = snap(tick_offset, VEC(), VEC(1, 1))
        self.float_offset += tick_offset * self.follow * self.manager.dt
        self.offset = intvec(self.float_offset)

class Player(VisibleSprite):
    def __init__(self, scene: Scene) -> None:
        super().__init__(scene, Layers.PLAYER)
        self.size = VEC(45, 60)
        self.pos = VEC(0, -100)
        self.vel = VEC(0, 0)
        self.acc = VEC(0, 0)
        self.speed = 150
        self.rect = pygame.Rect(self.pos, self.size)
        self.on_ground = False

        self.throwing = False
        self.sb_vel = VEC(0, 0)
        self.cooldown_time = time.time()
        self.snowball = None

        self.CONST_ACC = 500 # 500 pixels per second squared (physics :P)
        self.MAX_SPEED = 200
        self.JUMP_SPEED = -400
        self.THROW_SPEED = 900
        self.SB_OFFSET = self.size // 2 - (0, 10)
        self.THROW_COOLDOWN = 1

        self.camera = Camera(self, (0, 100), 5)

    def update(self) -> None:
        keys = pygame.key.get_pressed()

        self.acc = VEC(0, GRAVITY)
        if keys[K_a]: # Acceleration
            self.acc.x -= self.CONST_ACC
        elif self.vel.x < 0: # Deceleration
            self.acc.x += self.CONST_ACC
        if keys[K_d]:
            self.acc.x += self.CONST_ACC
        elif self.vel.x > 0:
            self.acc.x -= self.CONST_ACC

        if (keys[K_w] or keys[K_SPACE]) and self.on_ground:
            self.vel.y = self.JUMP_SPEED

        can_throw = time.time() - self.cooldown_time > self.THROW_COOLDOWN
        if pygame.mouse.get_pressed()[0] and can_throw:
            m_pos = VEC(pygame.mouse.get_pos())
            self.throwing = True
            # Use camera offset to convert screen-space pos to in-world pos
            try:
                self.sb_vel = -((m_pos - self.SB_OFFSET + self.camera.offset) - self.pos) * 8
                if self.sb_vel.length() > self.THROW_SPEED:
                    self.sb_vel.scale_to_length(self.THROW_SPEED)
            except ValueError:
                self.sb_vel = VEC() # 0 vector
        if MOUSEBUTTONUP in self.manager.events:
            if self.manager.events[MOUSEBUTTONUP].button == 1 and can_throw:
                self.cooldown_time = time.time()
                self.throwing = False
                self.snowball = Snowball(self.scene, self.sb_vel)

        self.vel += self.acc * self.manager.dt
        # _ to catch the successful clamp return value
        # Baiscally if it clamped to the left it would be -1, right would be 1, if it didn't clamp (value is in range), it's 0
        self.vel.x, _ = clamp(self.vel.x, -self.MAX_SPEED, self.MAX_SPEED)
        # If the absolute value of x vel is less than the constant acceleration, snap to 0 so that deceleration doesn't overshoot
        self.vel.x = snap(self.vel.x, 0, self.CONST_ACC * self.manager.dt)
        self.pos += self.vel * self.manager.dt

        self.rect.topleft = self.pos

        self.on_ground = False
        for y in sorted(Ground.sorted_instances.keys()): # Sort by highest ground first
            for ground in Ground.sorted_instances[y]:
                if not self.rect.colliderect(ground.rect): continue
                if self.rect.bottom < ground.rect.top + 2: # Snap to top if the player is just standing
                    self.pos.y = ground.rect.top - self.size.y
                else:
                    self.pos.y -= (self.rect.bottom - ground.rect.top) * 20 * self.manager.dt # Move up smoothly if stepping up
                self.vel.y = 0
                self.on_ground = True
                break
            else:
                continue # I hate this syntax :( but can't be bothered to make it better
            break

        if self.snowball:
            self.camera.master = self.snowball
            self.camera.follow = 2.5
            self.camera.extra_offset = VEC(0, 0)
        else:
            self.camera.master = self
            self.camera.follow = 4
            if self.throwing:
                self.camera.extra_offset = -VEC(self.sb_vel.x * 0.3, self.sb_vel.y * 0.05)
            else:
                self.camera.extra_offset = VEC(0, 200)
        self.camera.update()

    def draw(self) -> None:
        pygame.draw.rect(self.manager.screen, (255, 0, 0), (*(self.pos - self.camera.offset), *self.size))
        if not self.throwing: return
        factor = 0.015 # Basically how accurate we want the calculation to be, the distance factor between two points
        pos = self.pos + self.SB_OFFSET
        vel = self.sb_vel.copy()
        for i in range(60): # Number of points on the parabola that will be calculated
            vel.y += GRAVITY * factor
            vel += self.scene.wind_vel * factor
            pos += vel * factor
            if i % 3: continue # For every 4 calculated points, we draw 1 point
            pygame.draw.circle(self.manager.screen, (0, 0, 0), pos - self.camera.offset, 3)
