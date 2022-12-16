from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene
    from player import Player

from random import choices, uniform
import pygame

from .constants import VEC, GRAVITY, HEIGHT, STEP_WIDTH
from .sprite import VisibleSprite, Layers
from .ground import Ground
from . import assets

class SnowFlake(VisibleSprite):
    def __init__(self, scene: Scene, pos: tuple[int, int]) -> None:
        super().__init__(scene, Layers.SNOWFLAKE)
        
        self.pos = VEC(pos)
        self.vel = VEC(0, 0)
        self.resistance = uniform(0.85, 0.98)

        self.image = choices(assets.snowflakes, [10, 9, 8, 7, 3, 3, 2, 2, 1, 2])[0]
        self.size = VEC(self.image.get_size())
        self.rect = pygame.Rect(self.pos, self.size)

    def update(self) -> None:
        self.vel.y += GRAVITY * self.manager.dt
        self.vel += self.scene.wind * 5 * self.manager.dt
        self.vel *= self.resistance
        self.pos += self.vel * self.manager.dt

        self.rect.topleft = self.pos

        # Fast solution instead of looping through every single ground object
        try:
            if self.pos.y + self.size.y > Ground.height_map[self.pos.x // STEP_WIDTH * STEP_WIDTH]:
                self.kill()
                return
        except KeyError:
            pass
        if self.pos.y > 2000:
            self.kill()

    def draw(self) -> None:
        self.manager.screen.blit(self.image, self.rect.topleft - self.scene.player.camera.offset)