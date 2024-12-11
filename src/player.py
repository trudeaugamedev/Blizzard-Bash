from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from random import uniform, choice, randint
from math import sin, pi, ceil, cos
from pygame.locals import *
from typing import Optional
import pygame
import time

from .utils import intvec, snap, clamp, clamp_max, snap, sign, shadow, inttup
from .constants import VEC, SCR_DIM, GRAVITY, PIXEL_SIZE, TILE_SIZE
from .ground import Ground1, Ground2, Ground3
from .snowball import Snowball, SelfSnowball
from .sprite import VisibleSprite, Layers
from .swirl import Swirl, VortexSwirl
from .powerup import Powerup
from .border import Border
from .aura import Aura
from . import assets

class Camera:
    def __init__(self, scene: Scene, pos: tuple[int, int], follow: int):
        self.manager = scene.manager
        self.follow = follow
        self.float_offset = VEC(pos) - SCR_DIM // 2
        self.offset = intvec(self.float_offset)
        self.scene = scene

    def update(self, pos: tuple[int, int]):
        self.tick_offset = pos - self.offset - SCR_DIM // 2
        self.tick_offset = snap(self.tick_offset, VEC(), VEC(1, 1))
        self.float_offset += self.tick_offset * self.follow * self.manager.dt
        self.offset = intvec(self.float_offset)
        self.offset.y = max(self.scene.player.pos.y - 650, min(self.offset.y, -420))

class ThrowTrail(VisibleSprite):
    def __init__(self, scene: Scene, player: Player) -> None:
        super().__init__(scene, Layers.THROW_TRAIL)
        self.player = player

    def update(self) -> None:
        ...

    def draw(self) -> None:
        if not self.player.throwing: return
        factor = 0.01 # Basically how accurate we want the calculation to be, the distance factor between two points
        pos = VEC(self.player.rect.topleft) + self.player.SB_OFFSET
        vel = self.player.sb_vel.copy()
        for i in range(100): # Number of points on the parabola that will be calculated
            vel.y += GRAVITY * factor
            vel += self.scene.wind_vel * factor
            pos += vel * factor
            if i % 3: continue # For every 4 calculated points, we draw 1 point
            r = int((1 - i / 100) * 8)
            circle = pygame.Surface((r * 2 + 1, r * 2 + 1))
            pygame.draw.aacircle(circle, (i / 100 * 140 + 30,) * 3, (r, r), r, 3)
            self.manager.screen.blit(circle, pos - self.player.camera.offset - (r, r), special_flags=BLEND_RGB_SUB)

class DigProgress(VisibleSprite):
    def __init__(self, scene: Scene, player: Player) -> None:
        super().__init__(scene, Layers.GUI)
        self.player = player
        self.pos = player.pos + (0, 25)
        self.progress = 0

        self.snowball_img = assets.snowball_small[0]
        self.snowballs_displays = []
        self.num_snowballs = 0

    class SnowballDisplay:
        small = assets.snowball_small[0]
        small = small.subsurface(small.get_bounding_rect())
        large = assets.snowball_large[0]
        large = large.subsurface(large.get_bounding_rect())
        width_sum = 0
        x = 0

        def __init__(self, scene: Scene, player: Player, type: int) -> None:
            self.scene = scene
            self.player = player
            self.type = type
            self.image = [self.small, self.large, self.large][type]
            self.size = VEC(self.image.get_size())
            if type == 2:
                self.size.x += 26
                self.swirl = Swirl(scene, Layers.GUI, 52)

        def update(self) -> None:
            self.pos = self.player.pos + VEC(0, 65) - VEC(self.width_sum // 2, 0) - VEC(0, self.size.y // 2) + VEC(__class__.x, 0) + ((self.size.x - self.image.width) // 2, 0)
            __class__.x += self.size.x + 6

            if self.type == 2:
                self.swirl.pos = self.pos - ((self.size.x - self.image.width) // 2, self.size.y // 2)

        def draw(self) -> None:
            self.scene.manager.screen.blit(self.image, self.pos - self.player.camera.offset)

        def kill(self) -> None:
            if self.type == 2:
                self.swirl.kill()

    def update(self) -> None:
        if self.progress < 0.01:
            self.snowball_img = assets.snowball_large[0] if (self.player.dig_iterations + 1) % 3 == 0 else assets.snowball_small[0]
        if self.player.powerup == "rapidfire":
            self.snowball_img = assets.snowball_small[0]

        self.pos = self.player.pos + (0, 25) - (50, 3)
        if self.player.frame_group == self.player.assets.player_dig:
            progress = min((self.player.frame - 2) / 6, 1)
            self.progress += (progress - self.progress) * 15 * self.manager.dt
        else:
            self.progress -= self.progress * 25 * self.manager.dt

        DigProgress.SnowballDisplay.width_sum = 0
        for snowball in self.snowballs_displays:
            DigProgress.SnowballDisplay.width_sum += snowball.size.x + 6
        DigProgress.SnowballDisplay.width_sum -= 6
        DigProgress.SnowballDisplay.x = 0
        for snowball in self.snowballs_displays:
            snowball.update()

    def draw(self) -> None:
        rect = pygame.draw.rect(self.manager.screen, (0, 0, 0), (self.pos - (2, 2) - self.player.camera.offset, (104, 10)), 2)
        pygame.draw.rect(self.manager.screen, (255, 255, 255), (self.pos - self.player.camera.offset, (100, 6)))
        pygame.draw.rect(self.manager.screen, (0, 100, 220), (self.pos - self.player.camera.offset, (self.progress * 100, 6)))

        right = self.pos + (max(self.progress * 100, 0), 3) - self.player.camera.offset
        self.manager.screen.blit(self.snowball_img, right - VEC(self.snowball_img.size) // 2)

        if self.player.powerup != "rapidfire":
            for snowball in self.snowballs_displays:
                if snowball.type == 2:
                    snowball.swirl.visible = True
                snowball.draw()
        else:
            self.manager.screen.blit(assets.infinite_snowballs, rect.midbottom - VEC(assets.infinite_snowballs.get_width() // 2, 0) + (0, 16))
            for display in self.snowballs_displays:
                if display.type == 2:
                    display.swirl.visible = False

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
        self.overheat = 0
        # self.storms = []

        # Cheats
        self.infinite = False
        self.inf_type = ""
        self.funny_tele = False
        self.funny_cluster = False
        self.funny_rapid = False
        self.funny_strength = False
        self.no_kb = False
        self.no_move = False
        self.trigger_time = time.time() + 99999
        self.completely_lag = 0
        self.lag_time = time.time()
        # bot
        self.can_toggle_bot = False
        self.aimbot = False
        self.bot_mpos = VEC()
        self.bot_pressing = ""
        self.bot_target = VEC(99999, 0)
        self.dodging = False
        self.debug_brain = ""
        self.dodging_time = time.time()

        self.throw_trail = ThrowTrail(self.scene, self)
        self.throwing = False
        self.can_throw = True
        self.has_trigger = False
        self.just_triggered = False
        self.sb_vel = VEC(0, 0)
        self.snowball_queue = []
        self.snowballs: dict[Snowball] = {}
        self.rapidfire_time = time.time()
        self.aura = None

        self.frame_group = self.assets.player_idle
        self.frame = 0
        self.frame_time = time.time()

        self.first_start = True
        self.hit_strength = 0 # The strength another player's snowball hit the player
        self.hit_size = 0 # The size of the snowball that hit the player (1 for small, 2 for large)
        self.hit_powerup = None # The powerup the thrower of the snowball had when it hit the player

        self.self_snowball_time = time.time()

        self.CONST_ACC = 1300
        self.JUMP_SPEED1 = -400
        self.JUMP_SPEED2 = -320
        self.JUMP_SPEED3 = -210
        self.THROW_SPEED = 900
        self.SB_OFFSET = self.size // 2 - (0, 10)

        self.camera = Camera(self.scene, self.pos, 5)

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
        self.client.queue_data("powerup", ["rapidfire", "strength", "clustershot", "telekinesis"].index(self.powerup) if self.powerup else -1)

        snowballs = []
        for snowball in self.snowballs.values():
            data = {
                "id": snowball.id,
                "pos": inttup(snowball.pos),
                "frame": snowball.frame,
                "type": snowball.type,
            }
            snowballs.append(data)
        self.client.queue_data("snowballs", snowballs)

        # storms = []
        # for storm in self.storms:
        #     data = {
        #         "id": storm.id,
        #         "pos": inttup(storm.pos),
        #         "alpha": int(storm.alpha),
        #     }
        #     storms.append(data)
        # self.client.queue_data("storms", storms)

        # storm_blobs = []
        # for storm in self.storms:
        #     data = {
        #         "id": storm.id,
        #         "size": storm.image.size,
        #         "offsets": storm.offsets,
        #         "radii": storm.radii,
        #     }
        #     storm_blobs.append(data)
        # self.client.queue_data("storm_blobs", storm_blobs)

    def draw(self) -> None:
        self.manager.screen.blit(shadow(self.image), VEC(self.rect.topleft) - self.camera.offset + (3, 3), special_flags=BLEND_RGB_SUB)

        if self.powerup:
            color = {"rapidfire": (63, 134, 165), "strength": (233, 86, 86), "clustershot": (88, 210, 103), "telekinesis": (204, 102, 255)}[self.powerup]
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

        if (self.keys[K_SPACE] or self.bot_pressing.find(" space ") != -1) and self.on_ground and self.powerup != "rapidfire":
            self.digging = True
            self.idle = False
            self.throwing = False

        self.acc = VEC(0, GRAVITY)
        if self.keys[K_a] or self.bot_pressing.find(" a ") != -1: # Acceleration
            self.acc.x -= self.CONST_ACC
            self.flip = True
            if self.can_move:
                self.frame_group = self.assets.player_run
                if self.can_throw and self.next_snowball in {0, 3, 5}:
                    self.frame_group = self.assets.player_run_s
                elif self.can_throw:
                    self.frame_group = self.assets.player_run_l
                self.idle = False
        elif self.vel.x < 0: # Deceleration
            self.acc.x += self.CONST_ACC
            self.idle = True
        if self.keys[K_d] or self.bot_pressing.find(" d ") != -1:
            self.acc.x += self.CONST_ACC
            self.flip = False
            if self.can_move:
                self.frame_group = self.assets.player_run
                if self.can_throw and self.next_snowball in {0, 3, 5}:
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
        if self.keys[K_q] and self.can_toggle_bot and self.on_ground: # jump when toggling because I don't want to log keys
            self.aimbot = not self.aimbot
            self.bot_mpos = VEC()
            self.vel.y = self.JUMP_SPEED1
            self.on_ground = False
        if self.keys[K_p] and self.aimbot:
            print(self.debug_brain)

        if self.can_move:
            self.vel.x *= 0.004 ** self.manager.dt
        else:
            self.vel.x *= 0.00000005 ** self.manager.dt

        self.vel.x *= max(0, min(1, 1.12 - self.overheat / 25))
        self.overheat = max(0, self.overheat - 5 * self.manager.dt)

        if self.on_ground:
            self.jump_time = time.time()
        if (self.keys[K_w] or self.bot_pressing.find(" w ") != -1) and self.can_move and not self.digging:
            if time.time() - self.jump_time < 0.2:
                self.vel.y = self.JUMP_SPEED1
            elif time.time() - self.jump_time < 0.3:
                self.vel.y = self.JUMP_SPEED2
            elif time.time() - self.jump_time < 0.36:
                self.vel.y = self.JUMP_SPEED3
            self.jumping = True
            self.on_ground = False

        if (self.keys[K_s] or self.bot_pressing.find(" s ") != -1) and self.on_ground and self.ground_level in {Ground2, Ground3}:
            self.ground_level = Ground2 if self.ground_level == Ground3 else Ground1
            self.on_ground = False

        if self.keys[K_s] and not self.on_ground:
            self.acc.y += GRAVITY

    @property
    def next_snowball(self) -> Optional[int]:
        return self.snowball_queue[-1] if self.snowball_queue else None

    def update_throw(self) -> None:
        if self.completely_lag and time.time() - self.lag_time > 0.1:
            self.lag_time = time.time()
            for _ in range(int(self.completely_lag)):
                sb = Snowball(self.scene, (uniform(-100,100), -1000), 1, VEC())
                self.snowballs[sb.id] = sb
        if self.funny_rapid and self.powerup == "rapidfire" and time.time() - self.lag_time > 0.02:
            self.lag_time = time.time()
            sb = Snowball(self.scene, (uniform(-1000,1000), -2000), 1, self.pos + VEC(0, -self.size.y / 2))
            self.snowballs[sb.id] = sb

        if self.powerup != "rapidfire":
            self.can_throw = self.can_move and self.dig_iterations > 0
        else:
            self.can_throw = True
        if pygame.mouse.get_pressed()[0] or self.bot_pressing.find(" click ") != -1:
            if self.can_throw and not self.just_triggered:
                m_pos = VEC(pygame.mouse.get_pos())
                if self.bot_mpos != VEC():
                    m_pos = self.bot_mpos
                self.throwing = True
                if self.can_throw and self.next_snowball in {0, 3, 5}:
                    self.frame_group = self.assets.player_throw_s
                elif self.can_throw:
                    self.frame_group = self.assets.player_throw_l
                # Use camera offset to convert screen-space pos to in-world pos
                try:
                    self.sb_vel = ((m_pos - (self.SB_OFFSET - self.camera.offset)) - VEC(self.rect.topleft)) * 8
                    self.sb_vel.scale_to_length(self.THROW_SPEED)
                    if (self.powerup == "strength"):
                        self.sb_vel *= 2
                except ValueError:
                    self.sb_vel = VEC() # 0 vector
        if MOUSEBUTTONDOWN in self.manager.events or self.bot_pressing.find(" click ") != -1:
            if self.has_trigger:
                self.has_trigger = False
                self.just_triggered = True
                self.throwing = False
                for snowball in list(self.snowballs.values()):
                    snowball.trigger()
            elif self.can_throw and not self.just_triggered:
                m_pos = VEC(pygame.mouse.get_pos())
                if self.bot_mpos != VEC():
                    m_pos = self.bot_mpos
                self.throwing = True
                if self.can_throw and self.next_snowball in {0, 3, 5}:
                    self.frame_group = self.assets.player_throw_s
                elif self.can_throw:
                    self.frame_group = self.assets.player_throw_l
                # Use camera offset to convert screen-space pos to in-world pos
                try:
                    self.sb_vel = ((m_pos - (self.SB_OFFSET - self.camera.offset)) - VEC(self.rect.topleft)) * 8
                    self.sb_vel.scale_to_length(self.THROW_SPEED)
                    if (self.powerup == "strength"):
                        self.sb_vel *= 2
                except ValueError:
                    self.sb_vel = VEC() # 0 vector
        if MOUSEBUTTONUP in self.manager.events or self.bot_pressing.find(" click ") != -1:
            if (self.bot_pressing.find(" click ") != -1 or self.manager.events[MOUSEBUTTONUP].button == 1) and self.can_throw and not self.just_triggered:
                self.throwing = False
                assets.throw_sound.set_volume(0.2)
                assets.throw_sound.play()
                if self.powerup == "clustershot":
                    self.has_trigger = True
                    size = self.pop_snowball()
                    if size == 2:
                        sb = Snowball(self.scene, self.sb_vel, 2)
                        self.snowballs[sb.id] = sb
                        size -= 1
                    sb = Snowball(self.scene, self.sb_vel, 3 + size)
                    self.snowballs[sb.id] = sb
                elif self.powerup == "rapidfire":
                    sb = Snowball(self.scene, self.sb_vel, 0)
                    self.snowballs[sb.id] = sb
                    self.overheat = min(30, self.overheat + 1)
                else:
                    size = self.pop_snowball()
                    sb = Snowball(self.scene, self.sb_vel, size + (5 if self.powerup == "telekinesis" and size != 2 else 0))
                    self.snowballs[sb.id] = sb
                if self.powerup != "rapidfire":
                    self.dig_iterations -= 3 if (size == 1 or size == 2) else 1
                    self.can_throw = bool(self.snowball_queue)
                    if size == 2 or self.powerup == "telekinesis":
                        self.has_trigger = True
                else:
                    self.can_throw = True
            elif not self.has_trigger:
                self.just_triggered = False
                self.throwing = False
            elif len(self.snowballs) == 0:
                self.just_triggered = False
                self.throwing = False

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
        if self.no_move:
            self.vel.x = 0
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
            if not self.no_kb:
                self.vel.x = sign(self.hit_strength) * abs(self.hit_strength) * 100
            dscore = 0
            if self.hit_powerup not in {"rapidfire", "clustershot"}:
                dscore -= 2 # Penalty for getting hit (2 for now, may depend on self.hit_size)
            if self.hit_powerup == "strength":
                dscore -= 2 # lose another 2 points
            if dscore != 0:
                self.scene.spawn_hit_text(self.pos + (-sign(self.hit_strength) * 35, -self.size.y / 2), dscore)
            if not self.scene.waiting and not self.scene.eliminated:
                self.scene.score += dscore

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
                pos = self.pos - (0, 400) - self.scene.wind_vel * 0.25 + (self.vel.x * 0.4, 0) + (uniform(-80, 80), 0)
                sb = SelfSnowball(self.scene, VEC(0, 0), randint(0, 1), pos=pos, follow=False)
                self.snowballs[sb.id] = sb
                self.self_snowball_time = time.time()

        if self.powerup == "telekinesis":
            for snowball in self.snowballs.values():
                if (snowball.pos.distance_to(self.pos + VEC(0, -self.size.y / 2))) <= 250 and not snowball.stasis:
                    snowball.time_mult = 0.2
                    snowball.follow = False # temporarily remove follow because camera is acting weird

        # bot decision making
        if self.aimbot:
            self.bot_pressing = self.get_bot_decision()
        else:
            self.bot_pressing = ""

        self.can_move = self.frame_group != self.assets.player_dig and not self.digging

    # helper functions for decision making
    def left_of(self, o: float) -> bool:
        return self.pos.x < o
    def right_of(self, o: float) -> bool:
        return self.pos.x > o
    def close_to(self, o: VEC|float, dist: float) -> bool:
        if isinstance(o, VEC):
            return self.pos.distance_to(o) < dist
        return abs(self.pos.x - o) < dist

    def get_bot_decision(self) -> str:
        # TODO: shoot powerups
        min_dist = 99999
        min_snow_dist = 99999
        min_pwr_dist = 99999
        min_vortex_dist = 99999
        tracking_player = None
        tracking_snowball = None
        tracking_powerup: Powerup = None
        tracking_vortex: VortexSwirl = None
        returning = ""
        self.debug_brain = ""

        # avoid the border at all costs
        if self.right_of(Border.x):
            self.bot_target.x = Border.x - uniform(500, 1000)
        if self.left_of(-Border.x):
            self.bot_target.x = -Border.x + uniform(500, 1000)
        if self.bot_target.x != 99999:
            self.debug_brain += "run_away_border "
            if self.close_to(self.bot_target.x, 20):
                self.bot_target.x = 99999
                self.dodging = False
            elif self.right_of(self.bot_target.x):
                returning += " a w "
                if self.dodging == False: 
                    self.dodging_time = time.time()
                self.dodging = True
            else:
                returning += " d w "
                if self.dodging == False: 
                    self.dodging_time = time.time()
                self.dodging = True

        # find all relevant data
        # closest vortex
        for vortex in VortexSwirl.instances.values():
            if self.close_to(vortex.pos + (vortex.size / 2, vortex.size / 2), min_vortex_dist) and self.powerup == None:
                tracking_vortex = vortex
                min_vortex_dist = self.pos.distance_to(vortex.pos)
        # closest player
        for player in self.manager.other_players.values():
            if self.close_to(player.pos, min_dist) and \
               (tracking_vortex == None or \
               self.close_to(player.pos.x, abs(self.pos.x - (tracking_vortex.pos.x + vortex.size / 2))) or \
               sign(player.pos.x - self.pos.x) != sign(tracking_vortex.pos.x + vortex.size / 2 - self.pos.x)):
                tracking_player = player
                min_dist = self.pos.distance_to(player.pos)
            # closest snowball
            for snowball in list(player.snowballs.values()):
                if self.close_to(snowball.pos, min_snow_dist) and (tracking_vortex == None or snowball.pos.distance_to(tracking_vortex.pos + (vortex.size / 2, vortex.size / 2)) >= 250):
                    tracking_snowball = snowball
                    min_snow_dist = self.pos.distance_to(snowball.pos)
        # closest powerup
        for powerup in Powerup.instances.values():
            if self.close_to(powerup.pos, min_pwr_dist) and powerup.pos.y > -700 and \
               (tracking_vortex == None or \
               self.close_to(powerup.pos.x, abs(self.pos.x - tracking_vortex.pos.x)) or \
               sign(powerup.pos.x - self.pos.x) != sign(tracking_vortex.pos.x + vortex.size / 2 - self.pos.x)) :
                tracking_powerup = powerup
                min_pwr_dist = self.pos.distance_to(powerup.pos)

        # go for powerups when you don't have powerups
        if tracking_powerup != None and min_pwr_dist < 1500:
            is_tracking = tracking_player != None
            if is_tracking:
                closer_to_pwr = self.close_to(tracking_powerup.pos, tracking_powerup.pos.distance_to(tracking_player.pos))
                self_in_middle = sign(self.pos.x - tracking_powerup.pos.x) != sign(self.pos.x - tracking_player.pos.x)
                pwr_in_middle = sign(tracking_powerup.pos.x - self.pos.x) != sign(tracking_powerup.pos.x - tracking_player.pos.x)
            no_pwr = self.powerup == None
            if (not is_tracking or closer_to_pwr) or self_in_middle and no_pwr:
                self.debug_brain += "tracking_powerup "
                if self.left_of(tracking_powerup.pos.x):
                    returning += " d "
                else:
                    returning += " a "
            elif not is_tracking or pwr_in_middle:
                # roll a small snowball
                if len(self.snowball_queue) == 0 or self.snowball_queue[-1] != 0 and len(self.snowball_queue) < 5:
                    returning += " space "
                elif not self.close_to(tracking_powerup.pos.x, 250 if self.powerup != "strength" else 600):
                    if self.left_of(tracking_powerup.pos.x):
                        returning += " d "
                    else:
                        returning += " a "                    
                # try shooting the powerup
                else:
                    self.bot_mpos = (tracking_powerup.pos - self.camera.offset)
                    self.bot_mpos -= VEC(0, abs(tracking_powerup.pos.x - self.pos.x)) / 6
                    if self.powerup == "strength": # less distance-based adj.
                        self.bot_mpos += VEC(0, abs(tracking_player.pos.x - self.pos.x)) / 10
                    returning += " click "


        # dodging logic
        if tracking_snowball != None:
            # don't jump with telekinesis, you won't need to
            if self.powerup == "telekinesis" and abs(tracking_snowball.pos.x - self.pos.x) < 225:
                returning += " a " if self.left_of(tracking_snowball.pos.x) else " d "
                if self.dodging == False: 
                    self.dodging_time = time.time()
                self.dodging = True
            # dodge if you don't have a powerup that needs rolling
            if self.powerup != "strength" and self.powerup != "clustershot":
                if abs(tracking_snowball.pos.x - self.pos.x) < 275 and not tracking_snowball.pos.y - self.pos.y < -100:
                    returning += " w "
                    if self.dodging == False: 
                        self.dodging_time = time.time()
                    self.dodging = True
                    # dodge away from player
                    if self.left_of(tracking_snowball.pos.x):
                        returning += " a "
                    else:
                        returning += " d "
                else:
                    self.dodging = False
            else:
                self.dodging = False
        else:
            self.dodging = False
        if self.dodging:
            self.debug_brain += "dodging "

        # prevent bot from being stunlocked from dodging
        if self.dodging and time.time() - self.dodging_time > 8:
            returning = ""
            self.bot_target.x = 99999
            self.dodging_time = time.time()

        # trigger powerups if possible
        if tracking_player != None and time.time() - self.trigger_time >= (1.5 if self.powerup == "telekinesis" else 0.1 if self.powerup == "clustershot" else 99999):
            self.bot_mpos = (tracking_player.pos - VEC(0, self.size.y) - self.camera.offset)
            self.trigger_time = time.time() + 99999
            return returning + " click "

        # before going into attacks, finish powerup logic (go to bottom level to grab powerups)
        if returning != "":
            return returning + " s "

        # attacking logic
        if tracking_player != None:
            # run away from rapidfire or cluster or strength holders unless owning a close-range powerup yourself
            if (tracking_player.powerup >= 0 and tracking_player.powerup <= 2) and self.powerup not in ["strength", "telekinesis"] and min_dist < 750:
                self.debug_brain += "running_from_power_user(distance = " + str(min_dist) + ")"
                if self.powerup == None or self.dig_iterations < 4:
                    if self.left_of(tracking_player.pos.x):
                        return returning + " a " + (" space " if min_dist > 300 else "")
                    else:
                        return returning + " d " + (" space " if min_dist > 300 else "")
            # dig when you don't have a large snowball, dig while walking away from closest player
            if self.dig_iterations < 3 and self.powerup != "rapidfire" and not self.dodging:
                self.debug_brain += "digging "
                if self.powerup != "clustershot" and min_dist < 300 and not self.close_to(Border.x, 100) and not self.close_to(-Border.x, 100):
                    if self.left_of(player.pos.x):
                        returning += " a "
                    else:
                        returning += " d "
                return returning + " space "
            # start shooting at a certain range
            if min_dist < (2000 if self.powerup == "telekinesis" else \
                                600 if self.powerup == "strength" else \
                                250 if self.powerup == "rapidfire" else 300):
                self.bot_mpos = (tracking_player.pos - VEC(0, self.size.y) - self.camera.offset)
                self.bot_mpos -= VEC(0, abs(tracking_player.pos.x - self.pos.x)) / 6

                self.debug_brain += "in_shooting_range "

                # aim adjustment due to powerups
                if self.powerup == "clustershot": # aim slightly higher
                    self.bot_mpos -= VEC(0, 15)
                if self.powerup == "strength": # less distance-based adj.
                    self.bot_mpos += VEC(0, abs(tracking_player.pos.x - self.pos.x)) / 10
                    if self.close_to(tracking_player.pos.x, 100):
                        self.bot_mpos = (tracking_player.pos - VEC(0, self.size.y) - self.camera.offset)
                if self.powerup == "telekinesis": # aim a lot higher
                    self.bot_mpos -= VEC(0, 1000)

                # account for wind when target too high
                if tracking_player.pos.y - self.pos.y < -150 and self.close_to(tracking_player.pos.x, 100):
                    self.bot_mpos -= VEC(self.scene.wind_vel * 0.1, 0)

                returning += " click "
                # # too close, move further away
                # if (min_dist < (0 if self.powerup == "rapidfire" else 150)) and \
                #    tracking_player.pos.y - self.pos.y > -50 or \
                #    (self.powerup == "strength" and min_dist < 250):
                #     if self.left_of(tracking_player.pos.x):
                #         returning = " a "
                #     else:
                #         returning = " d "
            elif not self.dodging:
                self.debug_brain += "following_player "
                if self.left_of(tracking_player.pos.x): # move toward tracking player
                    returning += " d "
                else:
                    returning += " a "
            if tracking_player.pos.y - self.pos.y < -50 or (self.powerup != None and tracking_player.pos.y - self.pos.y < 50): # jump up if target too high or if you have powerup
                returning += " w "
            if tracking_player.pos.y - self.pos.y > 100 if self.powerup == None else 150: # drop down if target too low
                returning += " s "
        else: # more snowballs if no target
            self.debug_brain += "no_target "
            return " space "
        if self.powerup == "telekinesis" or self.powerup == "clustershot":
            self.trigger_time = time.time()
        return returning

    def add_snowball(self, size: int) -> None:
        self.snowball_queue.append(size)
        self.dig_progress.snowballs_displays.append(self.dig_progress.SnowballDisplay(self.scene, self, size))

    def spawn_snowball(self, size: int, pos: tuple[int, int], vel: tuple[int, int], follow: bool = True) -> None:
        sb = Snowball(self.scene, VEC(vel), size, pos=pos, follow=follow)
        self.snowballs[sb.id] = sb

    def pop_snowball(self) -> int:
        size = self.snowball_queue.pop()
        self.dig_progress.snowballs_displays.pop().kill()
        return size

    def update_image(self) -> None:
        if self.throwing:
            self.flip = self.sb_vel.x < 0

        if self.idle and not self.throwing and self.frame_group not in {self.assets.player_throw_l, self.assets.player_throw_s}:
            self.frame_group = self.assets.player_idle
            if self.can_throw and self.next_snowball in {0, 3, 5}:
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
            if time.time() - self.frame_time > (0.1 if self.dig_iterations < 3 else (self.dig_iterations - 2) * 0.05 + 0.1):
                # 0 - 9 frames, repeat fram 4 - 8
                self.frame_time = time.time()
                self.frame += 1
                if self.frame > 8:
                    if (not self.keys[K_SPACE] and not self.aimbot) or (self.bot_pressing.find(" space ") == -1 and self.aimbot):
                        self.digging = False
                        self.can_throw = True
                    else:
                        self.frame = 4
                        self.dig_progress.progress = 0
                    self.dig_iterations += 1
                    if (len(self.snowball_queue) > 0 and self.snowball_queue[-1] == 0) and (len(self.snowball_queue) > 1 and self.snowball_queue[-2] == 0):
                        self.pop_snowball()
                        self.pop_snowball()
                        self.add_snowball(1) # large snowball
                    else:
                        self.add_snowball(0) # small snowball
                elif self.frame <= 7:
                    if (not self.keys[K_SPACE] and not self.aimbot) or (self.bot_pressing.find(" space ") == -1 and self.aimbot):
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
                        if self.can_throw and self.next_snowball in {0, 3, 5}:
                            self.frame_group = self.assets.player_idle_s
                        elif self.can_throw:
                            self.frame_group = self.assets.player_idle_l

        if self.frame >= self.frame_group.length:
            self.frame = self.frame_group.length - 1

        self.orig_image = self.frame_group[self.frame]
        self.upright_image = pygame.transform.flip(self.orig_image, self.flip, False)
        self.image = pygame.transform.rotate(self.upright_image, self.rotation)

        self.rect = self.image.get_rect(midbottom=self.pos)
        self.real_rect.midbottom = self.rect.midbottom

    def update_powerup(self) -> None:
        if not self.infinite:
            if self.powerup is None: return
            self.powerup_max_time = {"rapidfire": 8, "strength": 16, "clustershot": 12, "hailstorm": 0, "telekinesis": 20}[self.powerup]
            if time.time() - self.powerup_time > self.powerup_max_time:
                if self.powerup != None:
                    self.powerup = None
        else:
            self.powerup = self.inf_type

        if self.powerup == "telekinesis" and self.aura is None:
            self.aura = Aura(self.scene, self)
        elif self.powerup != "telekinesis" and self.aura is not None:
            self.aura.kill()
            self.aura = None

    def update_camera(self) -> None:
        if self.snowballs:
            snowballs = list(self.snowballs.values())
            i = len(snowballs) - 1
            last = snowballs[i]
            while isinstance(last, SelfSnowball) or not last.follow:
                i -= 1
                if i < 0:
                    break
                last = snowballs[i]
        if not self.snowballs or isinstance(last, SelfSnowball) or not last.follow:
            self.camera.follow = 3
            pos = self.pos - (0, self.pos.y * 0.4 + 140)
            if self.throwing:
                pos += VEC(self.sb_vel.x * (0.15 if self.powerup != "strength" else 0.3), 0)
            self.camera.update(pos)
        else:
            self.camera.follow = 2.5
            if last.type in {5, 6}:
                diff = (last.pos - self.pos) / 2
                diff.y *= 0.6
                pos = self.pos + diff.clamp_magnitude(500, 1200)
            else:
                diff = (last.pos - self.pos) / 2
                pos = self.pos + diff.clamp_magnitude(450)
            self.camera.update(pos)
