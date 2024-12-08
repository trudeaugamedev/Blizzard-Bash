from __future__ import annotations
from typing import TYPE_CHECKING

import pygame.gfxdraw
if TYPE_CHECKING:
    from scene import Scene
    from player import Player

from random import randint, choice, uniform
from pygame.locals import BLEND_RGB_SUB
from math import atan, degrees, pi
from uuid import uuid4
import pygame
import time

from .constants import VEC, GRAVITY, PIXEL_SIZE
from .sprite import VisibleSprite, Layers
from .swirl import Swirl, VortexSwirl
from .utils import shadow, sign
from .powerup import Powerup
from .ground import Ground1
# from .storm import Storm
from . import assets

class Snowball(VisibleSprite):
    def __init__(self, scene: Scene, vel: tuple[float, float], sb_type: int, pos: VEC = None, follow: bool = True, stasis: bool = False) -> None:
        super().__init__(scene, Layers.SNOWBALL)
        self.id = uuid4().hex

        self.player: Player = self.scene.player # Type annotation just bcs I need intellisense lol
        self.pos = self.player.rect.topleft + self.player.SB_OFFSET if pos is None else pos
        self.vel = VEC(vel)
        self.acc = VEC(0, 0)
        self.time_mult = 1
        self.size = VEC(0, 0)
        self.frame = 0
        self.frame_time = time.time()
        self.type = sb_type
        self.frames = [assets.snowball_small, assets.snowball_large, assets.snowball_large, # normal snowballs
                       assets.snowball_small, assets.snowball_large, # clusters
                       assets.snowball_small, assets.snowball_large][sb_type] # strengths
        self.score = 1 if self.frames == assets.snowball_small else 4
        self.image = self.frames[self.frame]
        self.rect = self.image.get_rect(center=self.pos)
        self.real_rect = pygame.Rect(0, 0, *(10, 10) if self.frames == assets.snowball_large else (7, 7))
        self.real_rect.center = self.rect.center
        self.landed = False
        self.rotation = 0
        self.rot_speed = choice([randint(-400, -100), randint(100, 400)])
        self.hit_player = None
        self.follow = follow
        # self.is_storm = is_storm
        self.stasis = stasis
        self.really_follow = False
        self.start_time = time.time()

        if self.type == 2:
            self.swirl = Swirl(self.scene, Layers.SNOWBALL, 64)

    def update(self) -> None:
        self.image = self.frames[self.frame]
        self.rect = self.image.get_rect(center=self.pos)

        if self.landed:
            if time.time() - self.frame_time > 0.08:
                self.frame_time = time.time()
                self.frame += 1
                if self.frame == self.frames.length:
                    self.scene.player.snowballs.pop(self.id)
                    self.client.irreg_data.put({"landed": 1, "snowball_id": self.id, "player_id": self.client.id})
                    super().kill()
            return

        self.rotation += self.rot_speed * self.manager.dt
        self.image = pygame.transform.rotate(self.frames[self.frame], self.rotation)

        # self.acc = VEC(0, GRAVITY) * (0.4 if self.is_storm else 1)
        # self.acc += self.scene.wind_vel * (0.1 if self.is_storm else 1)
        self.acc = VEC(0, GRAVITY)
        self.acc += self.scene.wind_vel
        if self.stasis: self.acc = VEC()
        if self.really_follow:
            m_pos = VEC(pygame.mouse.get_pos())
            self.vel = ((m_pos + self.scene.player.camera.offset) - (self.pos - self.size / 2)).normalize() * 1000

        self.vel += self.acc * self.manager.dt * self.time_mult
        self.pos += self.vel * self.manager.dt * self.time_mult
        self.time_mult = 1
        self.rect = self.image.get_rect(center=self.pos)
        self.real_rect.center = self.rect.center

        if self.pos.y < -900:
            self.follow = False
        if abs(self.pos.x - self.scene.player.pos.x) > 2400:
            self.follow = False

        if self.stasis and time.time() - self.start_time > 20: # 20 sec lifespan
            self.kill()

        try:
            ground_y = Ground1.height_map[int(self.rect.centerx // PIXEL_SIZE * PIXEL_SIZE)]
        except KeyError:
            self.kill()
            return
        if self.pos.y > ground_y:
            self.kill()
            return

        if self.collide():
            return

        # if not self.is_storm:
        for powerup in Powerup.instances.values():
            if powerup.rect.colliderect(self.real_rect) and not powerup.touched:
                if powerup.type == "hailstorm":
                    self.scene.player.add_snowball(2)
                    self.scene.player.dig_iterations += 3
                else:
                    self.player.powerup = powerup.type
                    self.player.powerup_time = time.time()
                self.client.irreg_data.put({"id": powerup.id, "powerup": 1}) # powerup key to uniquify the message
                powerup.touched = True

        if self.type == 2:
            self.swirl.pos = self.pos - VEC(32, 32)

        if self.pos.distance_to(self.scene.player.pos) > 2400:
            self.follow = False

        if self.pos.y > 1000:
            self.kill()

    def collide(self) -> bool:
        for player in self.manager.other_players.values():
            if player.real_rect.colliderect(self.real_rect):
                sound = choice(assets.hit_sounds)
                sound.set_volume(self.score ** 2 * 0.2)
                sound.play()
                self.scene.hit = True
                self.scene.hit_pos = self.pos
                self.hit_player = player
                self.kill()
                if not self.scene.waiting and not self.scene.eliminated:
                    self.scene.score += self.score * (2 if self.player.powerup == "strength" else 1)
                    self.client.queue_data("score", self.scene.score)
                hit_strength = (2 + self.score + (4 * self.score + 6 if self.player.powerup == "strength" else 0)) * sign(self.vel.x) # LOT of knockback if strength (temporary?)
                self.client.irreg_data.put({
                    "hit": hit_strength,
                    "hit_size": 1 if self.frames == assets.snowball_small else 2,
                    "hit_powerup": self.player.powerup,
                    "id": player.id
                })
                return True
        return False

    arrowhead = pygame.Surface((21, 16), pygame.SRCALPHA)
    pygame.draw.polygon(
        arrowhead,
        (204, 102, 255),
        [(3, 0),
        (3, 16),
        (21, 8)]
    )

    def draw(self) -> None:
        if self.type == 5 or self.type == 6:
            w = 21 # This is actually the extra width that the surface needs to be extended by to fit both the width of the line and the arrowhead
            mpos = VEC(pygame.mouse.get_pos()) + self.scene.player.camera.offset
            start = self.pos - self.scene.player.camera.offset
            end = self.pos + (mpos - self.pos).normalize() * 80 - self.scene.player.camera.offset
            trans_surf = pygame.Surface((abs(end.x - start.x) + w, abs(end.y - start.y) + w), pygame.SRCALPHA)
            topleft = VEC(min(start.x, end.x), min(start.y, end.y))
            pygame.draw.line(trans_surf, (204, 102, 255), start - topleft + (w / 2,) * 2, end - topleft + (w / 2,) * 2, 6) # width of the line is actually 6
            # arrowhead
            diff = end - start
            head_img = pygame.transform.rotate(self.arrowhead, degrees(-atan(diff.y / diff.x) if diff.x > 0 else pi - atan(diff.y / diff.x)))
            trans_surf.blit(head_img, end - VEC(head_img.size) / 2 - topleft + (w / 2,) * 2)
            trans_surf.set_alpha(160)
            self.manager.screen.blit(trans_surf, topleft - (w / 2,) * 2)

        self.manager.screen.blit(shadow(self.image), VEC(self.rect.topleft) - self.scene.player.camera.offset + (3, 3), special_flags=BLEND_RGB_SUB)
        if self.scene.eliminated:
            self.image.set_alpha(80)
        self.manager.screen.blit(self.image, VEC(self.rect.topleft) - self.player.camera.offset)
        self.image.set_alpha(255)

    def kill(self) -> None:
        if self.type == 2:
            try:
                self.swirl.kill()
            except:
                pass
            # size = VEC(600 + randint(-50, 50), 250 + randint(-50, 50))
            # y = 800 + (self.pos.y - 40) * 0.6
            # storm = Storm(self.scene, self.id, self.pos - (size.x / 2, y) + VEC(randint(-80, 80), randint(-20, 20)), size, self.hit_player)
            VortexSwirl(self.scene, Layers.SNOWBALL, self.pos - (64, 64), 128, 20)
        if self.type not in {0, 1}:
            self.scene.player.has_trigger = False
        self.landed = True

    def trigger(self) -> None:
        if self.type == 2: # vortex
            self.kill()

        if self.type == 3 or self.type == 4: # cluster
            for _ in range(4 if self.type == 3 else 7):
                sb = Snowball(self.scene, self.vel + VEC(uniform(-180, 180), uniform(-180, 180)), 0, self.pos.copy())
                self.scene.player.snowballs[sb.id] = sb
            for _ in range(1 if (self.type == 3) else 3):
                sb = Snowball(self.scene, self.vel + VEC(uniform(-180, 180), uniform(-180, 180)), 1, self.pos.copy())
                self.scene.player.snowballs[sb.id] = sb

            # funny cluster?
            if self.scene.player.funny_cluster:
                for _ in range (30):
                    sb = Snowball(self.scene, VEC(uniform(-1, 1), uniform(-1, 1)).normalize() * 500, self.type - 3, self.pos.copy())
                    self.scene.player.snowballs[sb.id] = sb
            self.kill()

            Wave(self.scene, self.pos, (88, 210, 103))

        if self.type == 5 or self.type == 6: # telekinesis
            m_pos = VEC(pygame.mouse.get_pos() if not self.scene.player.aimbot else self.scene.player.bot_mpos)
            self.vel = ((m_pos + self.scene.player.camera.offset) - self.pos).normalize() * 1500
            self.start_time = time.time() # reset lifespan lol
            self.stasis = True
            self.type -= 5

            # funny telekinesis cuz why not
            if self.scene.player.funny_tele:
                self.really_follow = True

            Wave(self.scene, self.pos, (204, 102, 255))

class SelfSnowball(Snowball):
    def collide(self) -> bool:
        if self.scene.player.real_rect.colliderect(self.real_rect):
            sound = choice(assets.hit_sounds)
            sound.set_volume(self.score ** 2 * 0.2)
            sound.play()
            self.kill()
            self.scene.player.vel.x = self.score * choice([-1, 1]) * 100
            if not self.scene.waiting and not self.scene.eliminated:
                self.scene.score -= 1
            return True
        return False

class Wave(VisibleSprite):
    def __init__(self, scene: Scene, pos: VEC, color: tuple[int, int, int]) -> None:
        super().__init__(scene, Layers.SNOWBALL)
        self.pos = pos.copy()
        self.color = color
        self.radius = 0

    def update(self) -> None:
        self.radius += 220 * self.manager.dt
        if self.radius > 130:
            super().kill()

    def draw(self) -> None:
        r = int(self.radius)
        trans_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.aacircle(trans_surf, self.color + ((1 - self.radius / 130) * 200,), (r, r), r, 3 + int((1 - self.radius / 130) * 6))
        self.manager.screen.blit(trans_surf, self.pos - VEC(r, r) - self.scene.player.camera.offset)