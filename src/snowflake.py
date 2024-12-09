from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from random import choices, uniform, randint, choice
import pygame

from .constants import VEC, GRAVITY, PIXEL_SIZE, WIDTH
from .ground import Ground1, Ground2, Ground3
from .sprite import VisibleSprite, Layers
from . import assets

class SnowflakeRenderer(VisibleSprite):
    def __init__(self, scene: Scene, layer: Layers) -> None:
        super().__init__(scene, layer)
        self.snowflakes = []

    def update(self) -> None:
        ...

    def draw(self) -> None:
        self.manager.screen.fblits(map(lambda s: (s.image, s.pos - s.scene.player.camera.offset), self.snowflakes))
        self.snowflakes = []

# actually not visible, but just needs to be updated
class SnowFlake(VisibleSprite):
    def __init__(self, scene: Scene, pos: tuple[int, int]) -> None:
        super().__init__(scene, choice([Layers.SNOWFLAKE1, Layers.SNOWFLAKE2, Layers.SNOWFLAKE3]))
        if self._layer == Layers.SNOWFLAKE1:
            self.renderer = self.scene.snowflake_renderer1
            self.ground = Ground1
        elif self._layer == Layers.SNOWFLAKE2:
            self.renderer = self.scene.snowflake_renderer2
            self.ground = Ground2
        elif self._layer == Layers.SNOWFLAKE3:
            self.renderer = self.scene.snowflake_renderer3
            self.ground = Ground3

        self.pos = VEC(pos)
        self.vel = VEC(0, 0)
        self.resistance = uniform(0.0001, 0.0012)

        self.image = pygame.transform.rotate(choices(assets.snowflakes, [10, 9, 8, 7, 3, 3, 2, 2, 1, 2])[0], randint(0, 359))
        self.size = VEC(self.image.get_size())

    def update(self) -> None:
        self.vel.y += GRAVITY * self.manager.dt
        self.vel += self.scene.wind_vel * 5 * self.manager.dt
        self.vel *= self.resistance ** self.manager.dt
        self.pos += self.vel * self.manager.dt

        self.renderer.snowflakes.append(self)

        try:
            if self.pos.y + self.size.x / 2 > self.ground.height_map[self.pos.x // PIXEL_SIZE * PIXEL_SIZE]:
                self.kill()
                return
        except KeyError:
            pass
        if self.pos.y > 2000:
            self.kill()

    def draw(self) -> None:
        ...

    def kill(self) -> None:
        self.renderer.snowflakes.remove(self)
        super().kill()