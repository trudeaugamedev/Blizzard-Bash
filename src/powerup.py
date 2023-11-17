from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from pygame.locals import BLEND_RGB_SUB
import time

from .constants import VEC, GRAVITY, PIXEL_SIZE
from .sprite import VisibleSprite, Layers
from .ground import Ground
from .utils import shadow
from . import assets

class Powerup(VisibleSprite):
    instances = {}

    def __init__(self, scene: Scene, _id: int, pos: tuple[int, int]) -> None:
        super().__init__(scene, Layers.POWERUP)
        self.id = _id
        self.__class__.instances[self.id] = self
        if self.scene.powerup:
            try:
                self.scene.powerup.kill()
            except ValueError:
                pass
            self.scene.powerup = None
        self.image = assets.powerup_icon
        self.size = VEC(self.image.get_size())
        self.pos = VEC(pos)
        self.recv_pos = VEC(0, -800)
        self.vel = VEC(0, 0)

        self.initialized = True # Used to check whether the __init__ function has completed in the thread

    def update(self) -> None:
        if not hasattr(self, "initialized"): return

        self.pos = self.recv_pos

        ground_y = Ground.height_map[int(self.pos.x // PIXEL_SIZE * PIXEL_SIZE)]
        if self.pos.y > ground_y - self.size.y // 2:
            self.pos.y = ground_y - self.size.y // 2
            self.vel.x *= 0.85

        if self.pos.distance_to(VEC(self.scene.player.real_rect.center)) < 60:
            self.scene.player.powerup = True
            self.scene.player.powerup_time = time.time()
            self.client.irreg_data.put({"id": self.id, "powerup": 1}) # powerup key to distinguish the message

    def draw(self) -> None:
        if not hasattr(self, "initialized"): return
        self.manager.screen.blit(shadow(self.image), self.pos - self.size // 2 - self.scene.player.camera.offset + (3, 3), special_flags=BLEND_RGB_SUB)
        self.manager.screen.blit(self.image, self.pos - self.size // 2 - self.scene.player.camera.offset)

    def kill(self) -> None:
        self.scene.powerup = None
        super().kill()