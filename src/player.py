from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from pygame.locals import K_a, K_d, K_w, K_SPACE, MOUSEBUTTONUP, KEYDOWN
import pygame
import time

from .constants import VEC, SCR_DIM, GRAVITY, PIXEL_SIZE, TILE_SIZE
from .utils import intvec, snap, clamp, snap, sign
from .sprite import VisibleSprite, Layers
from .snowball import Snowball
from .ground import Ground
from . import assets

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
        self.orig_image = assets.player_idle[0]
        self.upright_image = self.orig_image
        self.image = self.upright_image
        self.rect = pygame.Rect(self.pos, self.size)
        self.real_rect = self.rect.copy()
        self.real_rect.size = (10 * PIXEL_SIZE, 20 * PIXEL_SIZE)
        self.on_ground = False
        self.ground = Ground.instances[int(self.pos.x // TILE_SIZE * TILE_SIZE)]
        self.flip = False
        self.rotation = 30

        self.digging = False
        self.can_move = True
        self.dig_iterations = 0

        self.powerup = False
        self.powerup_time = time.time()

        self.throwing = False
        self.sb_vel = VEC(0, 0)
        self.snowballs = []

        self.frame_group = assets.player_idle
        self.frame = 0
        self.frame_time = time.time()

        self.CONST_ACC = 500 # 500 pixels per second squared (physics :P)
        self.MAX_SPEED = 200
        self.JUMP_SPEED = -400
        self.THROW_SPEED = 900
        self.SB_OFFSET = self.size // 2 - (0, 10)

        self.camera = Camera(self, (0, 100), 5)

    def update(self) -> None:
        self.update_keys()
        self.update_throw()
        self.update_position()
        self.update_image()
        self.update_powerup()
        self.update_camera()

    def draw(self) -> None:
        self.manager.screen.blit(self.image, (*(VEC(self.rect.topleft) - self.camera.offset), *self.size))
        if not self.throwing: return
        factor = 0.015 # Basically how accurate we want the calculation to be, the distance factor between two points
        pos = VEC(self.rect.topleft) + self.SB_OFFSET
        vel = self.sb_vel.copy()
        for i in range(60): # Number of points on the parabola that will be calculated
            vel.y += GRAVITY * factor
            vel += self.scene.wind_vel * factor
            pos += vel * factor
            if i % 3: continue # For every 4 calculated points, we draw 1 point
            pygame.draw.circle(self.manager.screen, (0, 0, 0), pos - self.camera.offset, 3)

    def update_keys(self) -> None:
        keys = pygame.key.get_pressed()

        self.acc = VEC(0, GRAVITY)
        if keys[K_a] and self.can_move: # Acceleration
            self.acc.x -= self.CONST_ACC
            self.flip = True
        elif self.vel.x < 0: # Deceleration
            self.acc.x += self.CONST_ACC
        if keys[K_d] and self.can_move:
            self.acc.x += self.CONST_ACC
            self.flip = False
        elif self.vel.x > 0:
            self.acc.x -= self.CONST_ACC

        if keys[K_w] and self.on_ground:
            self.vel.y = self.JUMP_SPEED

        if KEYDOWN in self.manager.events and self.manager.events[KEYDOWN].key == K_SPACE:
            self.digging = not self.digging

    def update_throw(self) -> None:
        self.can_throw = True if self.powerup else not self.snowballs and self.can_move and self.dig_iterations
        if pygame.mouse.get_pressed()[0] and self.can_throw:
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
            if self.manager.events[MOUSEBUTTONUP].button == 1 and self.can_throw:
                self.cooldown_time = time.time()
                self.throwing = False
                self.snowballs.append(Snowball(self.scene, self.sb_vel, assets.snowball_small if self.dig_iterations < 3 or self.powerup else assets.snowball_large))
                self.dig_iterations = 0

    def update_position(self) -> None:
        self.vel += self.acc * self.manager.dt
        # _ to catch the successful clamp return value
        # Baiscally if it clamped to the left it would be -1, right would be 1, if it didn't clamp (value is in range), it's 0
        self.vel.x, _ = clamp(self.vel.x, -self.MAX_SPEED, self.MAX_SPEED)
        # If the absolute value of x vel is less than the constant acceleration, snap to 0 so that deceleration doesn't overshoot
        self.vel.x = snap(self.vel.x, 0, self.CONST_ACC * self.manager.dt)
        self.pos += self.vel * self.manager.dt

        self.on_ground = False
        ground_y = Ground.height_map[int(self.rect.centerx // PIXEL_SIZE * PIXEL_SIZE)]
        if self.pos.y > ground_y + 5:
            self.pos.y = ground_y + 5
            self.vel.y = 0
            self.on_ground = True

        self.can_move = self.frame_group != assets.player_dig

    def update_image(self) -> None:
        if self.throwing:
            self.flip = self.sb_vel.x < 0

        self.ground = Ground.instances[int(self.pos.x // TILE_SIZE * TILE_SIZE)]
        self.rotation += (self.ground.incline - self.rotation) * 8 * self.manager.dt
        self.rotation = snap(self.rotation, self.ground.incline, 1)

        if self.digging and self.on_ground:
            if self.frame == 0:
                self.dig_iterations = 0
            self.frame_group = assets.player_dig
            if time.time() - self.frame_time > 0.1:
                # 0 - 9 frames, repeat fram 4 - 8
                self.frame_time = time.time()
                self.frame += 1
                if self.frame > 8:
                    self.frame = 4
                    self.dig_iterations += 1
        elif self.frame_group == assets.player_dig:
            if time.time() - self.frame_time > 0.1:
                self.frame_time = time.time()
                self.frame += 1
                if self.frame >= self.frame_group.length:
                    self.frame_group = assets.player_idle
                    self.frame = 0
                    self.dig_iterations += 1

        self.orig_image = self.frame_group[self.frame]
        self.upright_image = pygame.transform.flip(self.orig_image, self.flip, False)
        self.image = pygame.transform.rotate(self.upright_image, self.rotation)

        self.rect = self.image.get_rect(midbottom=self.pos)
        self.real_rect.midbottom = self.rect.midbottom

    def update_powerup(self) -> None:
        if time.time() - self.powerup_time > 4 and self.powerup:
            self.powerup = False

        for player in self.manager.other_players.values():
            if not player.powerup: continue
            if player.powerup.pos.distance_to(VEC(self.real_rect.center)) < 60:
                self.powerup = True

    def update_camera(self) -> None:
        if self.snowballs and not self.powerup:
            self.camera.master = self.snowballs[-1]
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