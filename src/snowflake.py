from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from random import choices, uniform, randint, choice
import pygame

from .constants import VEC, GRAVITY, PIXEL_SIZE, WIDTH
from .ground import Ground, Ground2, Ground3
from .sprite import VisibleSprite, Layers
from . import assets

class SnowflakeRenderer(VisibleSprite):
    def __init__(self, scene: Scene, layer: Layers) -> None:
        super().__init__(scene, layer)
        self.snowflakes = []

    def update(self) -> None:
        ...

    def draw(self) -> None:
        self.manager.screen.fblits(self.snowflakes)
        self.snowflakes = []

# actually not visible, but just needs to be updated
class SnowFlake(VisibleSprite):
    def __init__(self, scene: Scene, pos: tuple[int, int]) -> None:
        super().__init__(scene, choice([Layers.SNOWFLAKE, Layers.SNOWFLAKE2, Layers.SNOWFLAKE3]))
        if self._layer == Layers.SNOWFLAKE:
            self.renderer = self.scene.snowflake_renderer1
            self.ground = Ground
        elif self._layer == Layers.SNOWFLAKE2:
            self.renderer = self.scene.snowflake_renderer2
            self.ground = Ground2
        elif self._layer == Layers.SNOWFLAKE3:
            self.renderer = self.scene.snowflake_renderer3
            self.ground = Ground3

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

        if -self.size.x < self.rect.left - self.scene.player.camera.offset.x < WIDTH:
            self.renderer.snowflakes.append((self.image, self.rect.topleft - self.scene.player.camera.offset))

        try:
            if self.rect.bottom > self.ground.height_map[self.pos.x // PIXEL_SIZE * PIXEL_SIZE]:
                self.kill()
                return
        except KeyError:
            pass
        if self.pos.y > 2000:
            self.kill()

    def draw(self) -> None:
        ...