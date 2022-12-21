from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene
    from player import Player

from random import choices, uniform, randint
import pygame

from .constants import VEC, GRAVITY, PIXEL_SIZE, WIDTH
from .sprite import VisibleSprite, Layers
from .ground import Ground
from . import assets

class SnowFlake(VisibleSprite):
    def __init__(self, scene: Scene, pos: tuple[int, int]) -> None:
        super().__init__(scene, Layers.SNOWFLAKE)
        
        self.pos = VEC(pos)
        self.vel = VEC(0, 0)
        self.resistance = uniform(0.85, 0.98)

        self.image = pygame.transform.rotate(choices(assets.snowflakes, [10, 9, 8, 7, 3, 3, 2, 2, 1, 2])[0], randint(0, 359))
        self.size = VEC(self.image.get_size())
        self.rect = pygame.Rect(self.pos, self.size)

    def update(self) -> None:
        self.vel.y += GRAVITY * self.manager.dt
        self.vel += self.scene.wind_vel * 5 * self.manager.dt
        self.vel *= self.resistance
        self.pos += self.vel * self.manager.dt

        self.rect.center = self.pos

        # Fast solution instead of looping through every single ground object
        try:
            if self.rect.bottom > Ground.height_map[self.pos.x // PIXEL_SIZE * PIXEL_SIZE]:
                self.kill()
                return
        except KeyError:
            pass
        if self.pos.y > 2000:
            self.kill()

    def draw(self) -> None:
        if self.rect.right - self.scene.player.camera.offset.x < 0 or self.rect.left - self.scene.player.camera.offset.x > WIDTH: return
        self.manager.screen.blit(self.image, self.rect.topleft - self.scene.player.camera.offset)