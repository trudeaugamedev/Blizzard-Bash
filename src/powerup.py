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
    def __init__(self, scene: Scene, pos: tuple[int, int]) -> None:
        super().__init__(scene, Layers.POWERUP)
        if self.scene.powerup:
            try:
                self.scene.powerup.kill()
            except ValueError:
                pass
            self.scene.powerup = None
        self.image = assets.powerup_icon
        self.size = VEC(self.image.get_size())
        self.pos = VEC(pos)
        self.vel = VEC(0, 0)

    def update(self) -> None:
        self.vel.y += GRAVITY * self.manager.dt
        self.vel += self.scene.wind_vel * 2 * self.manager.dt
        self.vel *= 0.99
        self.pos += self.vel * self.manager.dt

        ground_y = Ground.height_map[int(self.pos.x // PIXEL_SIZE * PIXEL_SIZE)]
        if self.pos.y > ground_y - self.size.y // 2:
            self.pos.y = ground_y - self.size.y // 2
            self.vel = VEC(0, 0)

        if self.pos.distance_to(VEC(self.scene.player.real_rect.center)) < 60:
            self.scene.player.powerup = True
            self.scene.player.powerup_time = time.time()
            self.kill()
            return
        for player in self.manager.other_players.values():
            if self.pos.distance_to(VEC(player.real_rect.center)) < 60:
                self.kill()
                return

    def draw(self) -> None:
        self.manager.screen.blit(shadow(self.image), self.pos - self.size // 2 - self.scene.player.camera.offset + (3, 3), special_flags=BLEND_RGB_SUB)
        self.manager.screen.blit(self.image, self.pos - self.size // 2 - self.scene.player.camera.offset)

    def kill(self) -> None:
        self.scene.powerup = None
        super().kill()