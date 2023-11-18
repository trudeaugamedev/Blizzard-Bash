from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from pygame.locals import *
from math import sin, pi
import pygame
import time

from .constants import VEC, SCR_DIM, GRAVITY, PIXEL_SIZE, TILE_SIZE, WIDTH
from .utils import intvec, snap, clamp, snap, sign, shadow, inttup
from .ground import Ground, Ground2, Ground3
from .sprite import VisibleSprite, Layers
from .snowball import Snowball
from . import assets

class Camera:
    def __init__(self, scene: Scene, pos: tuple[int, int], extra_offset: tuple[int, int], follow: int):
        self.manager = scene.manager
        self.extra_offset = VEC(extra_offset)
        self.follow = follow
        self.float_offset = VEC(pos) - SCR_DIM // 2 - extra_offset
        self.offset = intvec(self.float_offset)

    def update(self, pos: tuple[int, int]):
        self.tick_offset = pos - self.offset - SCR_DIM // 2 - self.extra_offset
        self.tick_offset = snap(self.tick_offset, VEC(), VEC(1, 1))
        self.float_offset += self.tick_offset * self.follow * self.manager.dt
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
        self.on_ground = False # on_ground is not stable
        self.jumping = True # which is why jumping needs to exist
        self.ground_level = Ground
        self.ground = self.ground_level.instances[int(self.pos.x // TILE_SIZE * TILE_SIZE)]
        self.flip = False
        self.rotation = 30
        self.idle = True

        self.digging = False
        self.can_move = True # Actually means if the player is digging
        self.dig_iterations = 0

        self.jump_time = time.time()
        
        self.powerup = False
        self.powerup_time = time.time()
        self.powerup_flash_time = time.time()

        self.throwing = False
        self.can_throw = True
        self.sb_vel = VEC(0, 0)
        self.snowballs: list[Snowball] = []

        self.frame_group = assets.player_idle
        self.frame = 0
        self.frame_time = time.time()

        self.first_start = True
        self.hit_strength = 0 # The strength another player's snowball hit the player
        self.eliminated = False

        self.CONST_ACC = 500 # 500 pixels per second squared (physics :P)
        self.MAX_SPEED = 200
        self.SMALL_MAX_SPEED = 30
        self.JUMP_SPEED1 = -400
        self.JUMP_SPEED2 = -320
        self.JUMP_SPEED3 = -210
        self.THROW_SPEED = 900
        self.SB_OFFSET = self.size // 2 - (0, 10)

        self.camera = Camera(self.scene, self.pos, (0, 100), 5)

    def update(self) -> None:
        self.update_keys()
        self.update_throw()
        self.update_position()
        self.update_image()
        self.update_powerup()
        self.update_camera()
        self.sync_data()
        self.first_start = False

    def sync_data(self) -> None:
        self.client.pers_data["pos"] = inttup(self.pos)
        self.client.pers_data["rot"] = int(self.rotation)
        self.client.pers_data["flip"] = self.flip
        self.client.pers_data["frame"] = assets.player.index(self.orig_image)

        snowballs = self.client.pers_data["snowballs"] = []
        for snowball in self.snowballs:
            data = {
                "pos": inttup(snowball.pos),
                "frame": snowball.frame,
                "type": int(snowball.type == assets.snowball_large),
            }
            snowballs.append(data)

    def draw(self) -> None:
        if self.powerup:
            alpha = (sin((time.time() - self.powerup_flash_time) * pi * 3) * 0.5 + 0.5) * 255
            mask = pygame.mask.from_surface(self.image)
            self.manager.screen.blit(mask.scale(VEC(mask.get_size()) + (20, 14)).to_surface(setcolor=(140, 230, 255, alpha), unsetcolor=(0, 0, 0, 0)), VEC(self.rect.topleft) - (10, 7) - self.camera.offset)

        self.manager.screen.blit(shadow(self.image), VEC(self.rect.topleft) - self.camera.offset + (3, 3), special_flags=BLEND_RGB_SUB)
        if self.eliminated:
            self.image.set_alpha(80)
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
        self.keys = pygame.key.get_pressed()

        self.acc = VEC(0, GRAVITY)
        if self.keys[K_a]: # Acceleration
            self.acc.x -= self.CONST_ACC
            self.flip = True
            if self.can_move:
                self.frame_group = assets.player_run
                if self.can_throw and self.dig_iterations < 3:
                    self.frame_group = assets.player_run_s
                elif self.can_throw:
                    self.frame_group = assets.player_run_l
                self.idle = False
        elif self.vel.x < 0: # Deceleration
            self.acc.x += self.CONST_ACC
            self.idle = True
        if self.keys[K_d]:
            self.acc.x += self.CONST_ACC
            self.flip = False
            if self.can_move:
                self.frame_group = assets.player_run
                if self.can_throw and self.dig_iterations < 3:
                    self.frame_group = assets.player_run_s
                elif self.can_throw:
                    self.frame_group = assets.player_run_l
                self.idle = False
        elif self.vel.x > 0:
            self.acc.x -= self.CONST_ACC
            self.idle = True
        if self.keys[K_a] and self.keys[K_d]:
            self.acc.x = -sign(self.vel.x) * self.CONST_ACC
            self.idle = True

        if self.on_ground:
            self.jump_time = time.time()
        if self.keys[K_w] and self.can_move:
            if time.time() - self.jump_time < 0.2:
                self.vel.y = self.JUMP_SPEED1
            elif time.time() - self.jump_time < 0.3:
                self.vel.y = self.JUMP_SPEED2
            elif time.time() - self.jump_time < 0.36:
                self.vel.y = self.JUMP_SPEED3
            self.jumping = True
            self.on_ground = False

        if self.keys[K_s] and self.on_ground and self.ground_level in {Ground2, Ground3}:
            self.pos.y += 10
            self.on_ground = False

        if self.keys[K_SPACE]:
            self.digging = True
            self.idle = False
            self.throwing = False

    def update_throw(self) -> None:
        self.can_throw = True if self.powerup else not self.snowballs and self.can_move and self.dig_iterations
        if pygame.mouse.get_pressed()[0] and self.can_throw:
            m_pos = VEC(pygame.mouse.get_pos())
            self.throwing = True
            if self.can_throw and self.dig_iterations < 3:
                self.frame_group = assets.player_throw_s
            elif self.can_throw:
                self.frame_group = assets.player_throw_l
            # Use camera offset to convert screen-space pos to in-world pos
            try:
                self.sb_vel = ((m_pos - self.SB_OFFSET + self.camera.offset) - self.pos) * 8
                if self.sb_vel.length() > self.THROW_SPEED:
                    self.sb_vel.scale_to_length(self.THROW_SPEED)
            except ValueError:
                self.sb_vel = VEC() # 0 vector
        if MOUSEBUTTONUP in self.manager.events:
            if self.manager.events[MOUSEBUTTONUP].button == 1 and self.can_throw:
                self.throwing = False
                self.snowballs.append(Snowball(self.scene, self.sb_vel, assets.snowball_small if self.dig_iterations < 3 or self.powerup else assets.snowball_large))
                self.dig_iterations = 0

    def update_position(self) -> None:
        self.vel += self.acc * self.manager.dt
        # _ to catch the successful clamp return value
        # Baiscally if it clamped to the left it would be -1, right would be 1, if it didn't clamp (value is in range), it's 0
        if self.can_move:
            self.vel.x, _ = clamp(self.vel.x, -self.MAX_SPEED, self.MAX_SPEED)
        else:
            self.vel.x, _ = clamp(self.vel.x, -self.SMALL_MAX_SPEED, self.SMALL_MAX_SPEED)
        # If the absolute value of x vel is less than the constant acceleration, snap to 0 so that deceleration doesn't overshoot
        self.vel.x = snap(self.vel.x, 0, self.CONST_ACC * self.manager.dt)
        self.pos += self.vel * self.manager.dt

        centerx = int(self.rect.centerx // PIXEL_SIZE * PIXEL_SIZE)
        if self.vel.y > 0:
            grounds = [Ground, Ground2, Ground3]
            highest = min(grounds, key=lambda g: g.height_map[centerx])
            grounds.remove(highest)
            middle = min(grounds, key=lambda g: g.height_map[centerx])
            grounds.remove(middle)
            lowest = grounds[0]
            highest_y, middle_y, lowest_y = highest.height_map[centerx], middle.height_map[centerx], lowest.height_map[centerx]
            above = lowest # Closest ground it is above
            if self.pos.y <= highest_y + 12:
                above = highest
            elif self.pos.y <= middle_y + 12:
                above = middle
            self.ground_level = above
            if highest is Ground or highest is Ground2 and above is Ground3:
                self.ground_level = Ground

        ground_y = self.ground_level.height_map[centerx]
        if self.pos.y > ground_y + 5:
            self.pos.y = ground_y + 5
            self.vel.y = 0
            self.on_ground = True
            self.jumping = False

        if self.hit_strength != 0:
            self.vel.x = self.hit_strength * 130
            self.hit_strength = 0

        self.pos.x, _ = clamp(self.pos.x, -2007, 2061)

        self.can_move = self.frame_group != assets.player_dig and not self.digging

    def update_image(self) -> None:
        if self.throwing:
            self.flip = self.sb_vel.x < 0

        if self.idle and not self.throwing and self.frame_group not in {assets.player_throw_l, assets.player_throw_s}:
            self.frame_group = assets.player_idle
            if self.can_throw and self.dig_iterations < 3:
                self.frame_group = assets.player_idle_s
            elif self.can_throw:
                self.frame_group = assets.player_idle_l

        try:
            self.ground = self.ground_level.instances[int(self.rect.centerx // TILE_SIZE * TILE_SIZE)]
        except KeyError:
            pass
        self.rotation += (self.ground.incline - self.rotation) * 8 * self.manager.dt
        self.rotation = snap(self.rotation, self.ground.incline, 1)

        # Play digging animations
        if self.digging and self.on_ground:
            self.frame_group = assets.player_dig
            if time.time() - self.frame_time > 0.1:
                # 0 - 9 frames, repeat fram 4 - 8
                self.frame_time = time.time()
                self.frame += 1
                if self.frame > 8:
                    if not self.keys[K_SPACE]:
                        self.digging = False
                        self.can_throw = True
                    else:
                        self.frame = 4
                    self.dig_iterations += 1
        # End player animations
        elif self.frame_group == assets.player_dig:
            if time.time() - self.frame_time > 0.1:
                self.frame_time = time.time()
                self.frame += 1
                if self.frame >= self.frame_group.length:
                    self.frame_group = assets.player_idle
                    self.idle = True
                    self.frame = 0
                    self.digging = False
        # Play running animations
        elif self.frame_group in {assets.player_run, assets.player_run_l, assets.player_run_s}:
            if time.time() - self.frame_time > 0.1:
                self.frame_time = time.time()
                self.frame += 1
                if self.frame >= self.frame_group.length:
                    self.frame = 0
        # Play throwing animations
        elif self.frame_group in {assets.player_throw_l, assets.player_throw_s}:
            if self.throwing:
                self.frame = 0
            else:
                if time.time() - self.frame_time > 0.1:
                    self.frame_time = time.time()
                    self.frame += 1
                    if self.frame >= self.frame_group.length:
                        self.idle = True

        if self.frame >= self.frame_group.length:
            self.frame = self.frame_group.length - 1

        self.orig_image = self.frame_group[self.frame]
        self.upright_image = pygame.transform.flip(self.orig_image, self.flip, False)
        self.image = pygame.transform.rotate(self.upright_image, self.rotation)

        self.rect = self.image.get_rect(midbottom=self.pos)
        self.real_rect.midbottom = self.rect.midbottom

    def update_powerup(self) -> None:
        if time.time() - self.powerup_time > 4 and self.powerup:
            self.powerup = False
            self.throwing = False

    def update_camera(self) -> None:
        if self.snowballs:
            self.camera.follow = 1.5
            self.camera.extra_offset = VEC((self.snowballs[-1].pos - self.pos) * self.snowballs[-1].pos.distance_to(self.pos) / 2500)
            self.camera.extra_offset.x -= self.vel.x * 2 if sign(self.camera.tick_offset.x) == -sign(self.vel.x) else 0
            self.camera.update(self.snowballs[-1].pos)
        else:
            self.camera.follow = 3
            if self.throwing:
                self.camera.extra_offset = -VEC(self.sb_vel.x * 0.15, 0)
            else:
                self.camera.extra_offset = VEC(0, 100)
            self.camera.update(self.pos - (0, 100))
