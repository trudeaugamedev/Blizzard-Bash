from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from random import uniform, choice
from math import sin, pi, sqrt
from pygame.locals import *
import pygame
import time

from .utils import intvec, snap, clamp, clamp_max, snap, sign, shadow, inttup
from .constants import VEC, SCR_DIM, GRAVITY, PIXEL_SIZE, TILE_SIZE
from .ground import Ground1, Ground2, Ground3
from .snowball import Snowball, SelfSnowball
from .sprite import VisibleSprite, Layers
from .border import Border
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

class ThrowTrail(VisibleSprite):
    def __init__(self, scene: Scene, player: Player) -> None:
        super().__init__(scene, Layers.THROW_TRAIL)
        self.player = player

    def update(self) -> None:
        ...

    def draw(self) -> None:
        if not self.player.throwing: return
        factor = 0.015 # Basically how accurate we want the calculation to be, the distance factor between two points
        pos = VEC(self.player.rect.topleft) + self.player.SB_OFFSET
        vel = self.player.sb_vel.copy()
        for i in range(60): # Number of points on the parabola that will be calculated
            vel.y += GRAVITY * factor
            vel += self.scene.wind_vel * factor
            pos += vel * factor
            if i % 3: continue # For every 4 calculated points, we draw 1 point
            pygame.draw.circle(self.manager.screen, (0, 0, 0), pos - self.player.camera.offset, 3)

class DigProgress(VisibleSprite):
    def __init__(self, scene: Scene, player: Player) -> None:
        super().__init__(scene, Layers.GUI)
        self.player = player
        self.pos = player.pos + (0, 25)
        self.progress = 0

    def update(self) -> None:
        self.pos = self.player.pos + (0, 25) - (50, 3)
        if self.player.frame_group == self.player.assets.player_dig:
            progress = min((self.player.frame - 2) / 6, 1)
            self.progress += (progress - self.progress) * 15 * self.manager.dt
        else:
            self.progress -= self.progress * 25 * self.manager.dt

    def draw(self) -> None:
        pygame.draw.rect(self.manager.screen, (0, 0, 0), (self.pos - (2, 2) - self.player.camera.offset, (104, 10)), 2)
        pygame.draw.rect(self.manager.screen, (255, 255, 255), (self.pos - self.player.camera.offset, (100, 6)))
        pygame.draw.rect(self.manager.screen, (0, 100, 220), (self.pos - self.player.camera.offset, (self.progress * 100, 6)))

class Player(VisibleSprite):
    def __init__(self, scene: Scene) -> None:
        super().__init__(scene, Layers.PLAYER1)
        self.size = VEC(45, 60)
        self.pos = VEC(0, -100)
        self.vel = VEC(0, 0)
        self.acc = VEC(0, 0)
        self.speed = 150
        self.clothes_hue = self.scene.previous_scene.skin_selector.clothes_hue
        self.hat_hue = self.scene.previous_scene.skin_selector.hat_hue
        self.skin_tone = self.scene.previous_scene.skin_selector.skin_tone
        self.assets = assets.PlayerAssets(self.clothes_hue, self.hat_hue, self.skin_tone)
        self.orig_image = self.assets.player_idle[0]
        self.upright_image = self.orig_image
        self.image = self.upright_image
        self.rect = pygame.Rect(self.pos, self.size)
        self.real_rect = self.rect.copy()
        self.real_rect.size = (10 * PIXEL_SIZE, 20 * PIXEL_SIZE)
        self.on_ground = False # on_ground is not stable
        self.jumping = True # which is why jumping needs to exist
        self.ground_level = Ground1
        self.ground = self.ground_level.instances[int(self.pos.x // TILE_SIZE * TILE_SIZE)]
        self.flip = False
        self.rotation = 30
        self.idle = True

        self.digging = False
        self.can_move = True # Actually means if the player is digging
        self.dig_iterations = 0
        self.dig_progress = DigProgress(self.scene, self)

        self.jump_time = time.time()

        self.powerup = None
        self.powerup_time = time.time()
        self.powerup_max_time = 0
        self.powerup_flash_time = time.time()

        self.throw_trail = ThrowTrail(self.scene, self)
        self.throwing = False
        self.can_throw = True
        self.sb_vel = VEC(0, 0)
        self.snowballs: list[Snowball] = []
        self.rapidfire_time = time.time()

        self.frame_group = self.assets.player_idle
        self.frame = 0
        self.frame_time = time.time()

        self.first_start = True
        self.hit_strength = 0 # The strength another player's snowball hit the player
        self.hit_size = 0 # The size of the snowball that hit the player (1 for small, 2 for large)
        self.hit_powerup = None # The powerup the thrower of the snowball had when it hit the player

        self.self_snowball_time = time.time()

        self.CONST_ACC = 500 # 500 pixels per second squared (physics :P)
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
        self.client.queue_data("pos", inttup(self.pos))
        self.client.queue_data("rot", int(self.rotation))
        self.client.queue_data("flip", self.flip)
        self.client.queue_data("frame", self.assets.player.index(self.orig_image))
        self.client.queue_data("powerup", ["rapidfire", "strength", "clustershot"].index(self.powerup) if self.powerup else -1)

        snowballs = []
        for snowball in self.snowballs:
            data = {
                "pos": inttup(snowball.pos),
                "frame": snowball.frame,
                "type": int(snowball.type == assets.snowball_large),
            }
            snowballs.append(data)
        self.client.queue_data("snowballs", snowballs)

    def draw(self) -> None:
        self.manager.screen.blit(shadow(self.image), VEC(self.rect.topleft) - self.camera.offset + (3, 3), special_flags=BLEND_RGB_SUB)

        if self.powerup:
            color = {"rapidfire": (63, 134, 165), "strength": (233, 86, 86), "clustershot": (78, 180, 93)}[self.powerup]
            alpha = (sin((time.time() - self.powerup_flash_time) * pi * 3) * 0.5 + 0.5) * 255
            mask = pygame.mask.from_surface(self.image)
            powerup_overlay = mask.scale(VEC(mask.get_size()) + (20, 14)).to_surface(setcolor=(*color, alpha), unsetcolor=(0, 0, 0, 0))
            self.manager.screen.blit(powerup_overlay, VEC(self.rect.topleft) - (10, 7) - self.camera.offset)

        if self.scene.eliminated:
            self.image.set_alpha(80)
        self.manager.screen.blit(self.image, (*(VEC(self.rect.topleft) - self.camera.offset), *self.size))
        self.image.set_alpha(255)

        if self.powerup:
            powerup_overlay.set_alpha(100)
            self.manager.screen.blit(powerup_overlay, VEC(self.rect.topleft) - (10, 7) - self.camera.offset)

    def update_keys(self) -> None:
        self.keys = pygame.key.get_pressed()

        self.acc = VEC(0, GRAVITY)
        if self.keys[K_a]: # Acceleration
            self.acc.x -= self.CONST_ACC
            self.flip = True
            if self.can_move:
                self.frame_group = self.assets.player_run
                if self.can_throw and self.dig_iterations < 3:
                    self.frame_group = self.assets.player_run_s
                elif self.can_throw:
                    self.frame_group = self.assets.player_run_l
                self.idle = False
        elif self.vel.x < 0: # Deceleration
            self.acc.x += self.CONST_ACC
            self.idle = True
        if self.keys[K_d]:
            self.acc.x += self.CONST_ACC
            self.flip = False
            if self.can_move:
                self.frame_group = self.assets.player_run
                if self.can_throw and self.dig_iterations < 3:
                    self.frame_group = self.assets.player_run_s
                elif self.can_throw:
                    self.frame_group = self.assets.player_run_l
                self.idle = False
        elif self.vel.x > 0:
            self.acc.x -= self.CONST_ACC
            self.idle = True
        if self.keys[K_a] and self.keys[K_d]:
            self.acc.x = -sign(self.vel.x) * self.CONST_ACC
            self.idle = True

        if self.can_move:
            self.vel.x *= 0.12 ** self.manager.dt
        else:
            self.vel.x *= 0.0001 ** self.manager.dt

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
            self.ground_level = Ground2 if self.ground_level == Ground3 else Ground1
            self.on_ground = False

        if self.keys[K_SPACE] and self.on_ground:
            self.digging = True
            self.idle = False
            self.throwing = False

    def update_throw(self) -> None:
        if self.powerup != "rapidfire":
            self.can_throw = self.can_move and self.dig_iterations > 0
        elif time.time() - self.rapidfire_time > 0.2:
            self.rapidfire_time = time.time()
            self.can_throw = True
        if pygame.mouse.get_pressed()[0] and self.can_throw:
            m_pos = VEC(pygame.mouse.get_pos())
            self.throwing = True
            if self.can_throw and self.dig_iterations < 3:
                self.frame_group = self.assets.player_throw_s
            elif self.can_throw:
                self.frame_group = self.assets.player_throw_l
            # Use camera offset to convert screen-space pos to in-world pos
            try:
                self.sb_vel = ((m_pos - self.SB_OFFSET + self.camera.offset) - self.pos) * 8 * (1.4 if self.powerup == "strength" else 1)
                if self.sb_vel.length() > self.THROW_SPEED * (1.4 if self.powerup == "strength" else 1):
                    self.sb_vel.scale_to_length(self.THROW_SPEED * (1.4 if self.powerup == "strength" else 1))
            except ValueError:
                self.sb_vel = VEC() # 0 vector
        if MOUSEBUTTONUP in self.manager.events:
            if self.manager.events[MOUSEBUTTONUP].button == 1 and self.can_throw:
                self.throwing = False
                assets.throw_sound.set_volume(0.2)
                assets.throw_sound.play()
                if self.powerup == "clustershot":
                    for _ in range(4 if self.dig_iterations < 3 else 7):
                        self.snowballs.append(Snowball(self.scene, self.sb_vel + VEC(uniform(-180, 180), uniform(-180, 180)), assets.snowball_small))
                    for _ in range(1 if self.dig_iterations < 3 else 3):
                        self.snowballs.append(Snowball(self.scene, self.sb_vel + VEC(uniform(-180, 180), uniform(-180, 180)), assets.snowball_large))
                else:
                    self.snowballs.append(Snowball(self.scene, self.sb_vel, assets.snowball_small if self.dig_iterations < 3 or self.powerup == "rapidfire" else assets.snowball_large))
                self.dig_iterations = 0
                self.can_throw = False

    def update_position(self) -> None:
        centerx = int(self.rect.centerx // PIXEL_SIZE * PIXEL_SIZE)
        grounds = [Ground1, Ground2, Ground3]
        highest = min(grounds, key=lambda g: g.height_map[centerx])
        grounds.remove(highest)
        middle = min(grounds, key=lambda g: g.height_map[centerx])
        grounds.remove(middle)
        lowest = grounds[0]
        highest_y, middle_y, _lowest_y = highest.height_map[centerx], middle.height_map[centerx], lowest.height_map[centerx]
        if self.jumping and self.pos.y < self.ground_level.height_map[centerx] - 5 and self.vel.y > 0:
            above = lowest # Closest ground it is above
            if self.pos.y < highest_y + 5:
                above = highest
            elif self.pos.y < middle_y + 5 and self.ground_level is not highest and highest is not Ground2:
                above = middle
            self.ground_level = above
        if highest is Ground1 or middle is Ground1 and self.ground_level is Ground2:
            self.ground_level = Ground1
        if highest is Ground2 and self.ground_level is Ground3 and self.pos.y < highest_y + 20:
            self.ground_level = Ground2

        if self.ground_level == Ground1 and self._layer != Layers.PLAYER1:
            self.scene.sprite_manager.remove(self)
            self._layer = Layers.PLAYER1
            self.scene.sprite_manager.add(self)
        elif self.ground_level == Ground2 and self._layer != Layers.PLAYER2:
            self.scene.sprite_manager.remove(self)
            self._layer = Layers.PLAYER2
            self.scene.sprite_manager.add(self)
        elif self.ground_level == Ground3 and self._layer != Layers.PLAYER3:
            self.scene.sprite_manager.remove(self)
            self._layer = Layers.PLAYER3
            self.scene.sprite_manager.add(self)

        self.vel += self.acc * self.manager.dt
        # If the absolute value of x vel is less than the constant acceleration, snap to 0 so that deceleration doesn't overshoot
        self.vel.x = snap(self.vel.x, 0, self.CONST_ACC * self.manager.dt)
        self.pos += self.vel * self.manager.dt

        ground_y = self.ground_level.height_map[centerx]
        if self.pos.y > ground_y + 5:
            self.pos.y = ground_y + 5
            self.vel.y = 0
            self.on_ground = True
            self.jumping = False
        if self.pos.y > Ground1.height_map[centerx] + 5:
            self.pos.y = Ground1.height_map[centerx] + 5
            self.vel.y = 0
            self.on_ground = True
            self.jumping = False

        if self.hit_strength != 0 or self.hit_size != 0:
            sound = choice(assets.hit_sounds)
            sound.set_volume(self.hit_strength ** 2 * 0.2)
            sound.play()
            self.vel.x = sign(self.hit_strength) * abs(self.hit_strength) * 100
            if not self.scene.waiting and not self.scene.eliminated:
                if self.hit_powerup not in {"rapidfire", "clustershot"}:
                    self.scene.score -= 1 # Penalty for getting hit (1 for now, may depend on self.hit_size)
            self.hit_strength = self.hit_size = 0
            self.hit_powerup = None

        if self.pos.x > Border.x:
            diff = self.pos.x - Border.x
            self.vel.x *= max(1 - diff / 800, 0) ** self.manager.dt
            if self.pos.x > Border.x + 800:
                self.pos.x = Border.x + 800
                self.vel.x = 0
        elif self.pos.x < -Border.x:
            diff = -self.pos.x - Border.x
            self.vel.x *= max(1 - diff / 800, 0) ** self.manager.dt
            if self.pos.x < -Border.x - 800:
                self.pos.x = -Border.x - 800
                self.vel.x = 0
        if self.pos.x > Border.x or self.pos.x < -Border.x:
            if time.time() - self.self_snowball_time > 800 / diff * 0.06:
                self.snowballs.append(SelfSnowball(self.scene, VEC(0, 0), choice([assets.snowball_small, assets.snowball_large])))
                self.snowballs[-1].pos = self.pos - (0, 400) - self.scene.wind_vel * 0.25 + (self.vel.x * 0.4, 0) + (uniform(-80, 80), 0)
                self.self_snowball_time = time.time()

        self.can_move = self.frame_group != self.assets.player_dig and not self.digging

    def update_image(self) -> None:
        if self.throwing:
            self.flip = self.sb_vel.x < 0

        if self.idle and not self.throwing and self.frame_group not in {self.assets.player_throw_l, self.assets.player_throw_s}:
            self.frame_group = self.assets.player_idle
            if self.can_throw and self.dig_iterations < 3:
                self.frame_group = self.assets.player_idle_s
            elif self.can_throw:
                self.frame_group = self.assets.player_idle_l

        try:
            self.ground = self.ground_level.instances[int(self.rect.centerx // TILE_SIZE * TILE_SIZE)]
        except KeyError:
            pass
        self.rotation += (self.ground.incline - self.rotation) * 8 * self.manager.dt
        self.rotation = snap(self.rotation, self.ground.incline, 1)

        # Play digging animations
        if self.digging and self.on_ground:
            self.frame_group = self.assets.player_dig
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
                        self.dig_progress.progress = 0
                    self.dig_iterations += 1
                elif self.frame <= 7:
                    if not self.keys[K_SPACE]:
                        self.frame_group = self.assets.player_idle
                        self.idle = True
                        self.frame = 0
                        self.digging = False
                        self.can_throw = True
        # End player animations
        elif self.frame_group == self.assets.player_dig:
            if time.time() - self.frame_time > 0.1:
                self.frame_time = time.time()
                self.frame += 1
                if self.frame >= self.frame_group.length:
                    self.frame_group = self.assets.player_idle
                    self.idle = True
                    self.frame = 0
                    self.digging = False
        # Play running animations
        elif self.frame_group in {self.assets.player_run, self.assets.player_run_l, self.assets.player_run_s}:
            if time.time() - self.frame_time > 0.1:
                self.frame_time = time.time()
                self.frame += 1
                if self.frame >= self.frame_group.length:
                    self.frame = 0
        # Play throwing animations
        elif self.frame_group in {self.assets.player_throw_l, self.assets.player_throw_s}:
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
        if self.powerup is None: return
        self.powerup_max_time = {"rapidfire": 7, "strength": 16, "clustershot": 10}[self.powerup]
        if time.time() - self.powerup_time > self.powerup_max_time:
            if self.powerup == "rapidfire":
                self.powerup = None
                self.throwing = False
            if self.powerup == "strength":
                self.powerup = None
            if self.powerup == "clustershot":
                self.powerup = None

    def update_camera(self) -> None:
        if self.snowballs:
            i = len(self.snowballs) - 1
            last = self.snowballs[i]
            while isinstance(last, SelfSnowball):
                i -= 1
                if i < 0:
                    break
                last = self.snowballs[i]
        if not self.snowballs or isinstance(last, SelfSnowball):
            self.camera.follow = 3
            if self.throwing:
                self.camera.extra_offset = -VEC(self.sb_vel.x * 0.15, 0)
            else:
                self.camera.extra_offset = VEC(0, self.pos.y * 0.3 + 80)
            self.camera.update(self.pos - (0, self.pos.y * 0.3 + 80))
        else:
            self.camera.follow = 1.5
            self.camera.extra_offset = VEC((last.pos - self.pos) * last.pos.distance_to(self.pos) / 2500)
            self.camera.extra_offset.x -= self.vel.x * 2 if sign(self.camera.tick_offset.x) == -sign(self.vel.x) else 0
            self.camera.update(last.pos)
