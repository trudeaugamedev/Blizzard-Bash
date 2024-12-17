from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from pygame.locals import BLEND_RGB_SUB
import pygame
import time

from .constants import VEC, PIXEL_SIZE, WIDTH
from .sprite import VisibleSprite, Layers
from .ground import Ground1
from .utils import shadow
from . import assets

class Powerup(VisibleSprite):
    instances = {}

    def __init__(self, scene: Scene, _id: int, _type: str, pos: tuple[int, int]) -> None:
        super().__init__(scene, Layers.POWERUP)
        self.id = _id
        self.type = _type
        self.image = assets.powerup_icons[self.type]
        self.shadow_image = shadow(self.image)
        self.size = VEC(self.image.get_size())
        self.pos = VEC(pos)
        self.rect = pygame.Rect(self.pos - (12, 12), self.size + (24, 24))
        self.recv_pos = VEC(0, -2500)
        self.vel = VEC(0, 0)
        self.touched = False

        self.initialized = True # Used to check whether the __init__ function has completed in the thread
        self.__class__.instances[self.id] = self

    def update(self) -> None:
        if not hasattr(self, "initialized"): return

        self.pos = self.recv_pos # so that the pos doesnt end up at (0, 0) at the beginning

        try:
            ground_y = Ground1.height_map[int(self.pos.x // PIXEL_SIZE * PIXEL_SIZE)]
        except KeyError:
            self.kill()
            return
        if self.pos.y > ground_y - self.size.y // 2:
            self.pos.y = ground_y - self.size.y // 2
            self.vel.x *= 0.85

        self.rect = pygame.Rect(self.pos - (12, 12), self.size + (24, 24))
        if self.rect.colliderect(self.scene.player.real_rect) and not self.touched and not self.scene.eliminated:
            self.scene.player.collected_powerups += 1
            # MODIFICATIONS TO THIS SECTION SHOULD BE REFLECTED IN snowball.py AS WELL or else throwing a snowball at the powerup will crash the game!!!
            if self.type == "hailstorm":
                self.scene.player.add_snowball(2)
                self.scene.player.dig_iterations += 3
            else:
                if self.scene.player.powerup == "rapidfire":
                    self.scene.player.throwing = False
                self.scene.player.powerup = self.type
                self.scene.player.powerup_time = time.time()
            self.client.irreg_data.put({"id": self.id, "powerup": 1}) # powerup key to uniquify the message
            self.touched = True

    def draw(self) -> None:
        if not hasattr(self, "initialized"): return
        while self.image.get_locked(): pass
        if self.rect.right - self.scene.player.camera.offset.x < -20 or self.rect.left - self.scene.player.camera.offset.x > WIDTH + 20: return
        self.manager.screen.blit(self.shadow_image, self.pos - self.size // 2 - self.scene.player.camera.offset + (3, 3), special_flags=BLEND_RGB_SUB)
        self.manager.screen.blit(self.image, self.pos - self.size // 2 - self.scene.player.camera.offset)
