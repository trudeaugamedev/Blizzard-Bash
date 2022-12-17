from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

import pygame

from .sprite import VisibleSprite, Layers
from .constants import VEC, FONT2
from . import assets

class OtherPlayer(VisibleSprite):
    def __init__(self, scene: Scene, pos: tuple[int, int]) -> None:
        super().__init__(scene, Layers.PLAYER)
        self.size = VEC(45, 60)
        self.pos = VEC(pos)
        self.rect = pygame.Rect(self.pos, self.size)
        self.snowball = None
        self.score = 0

    def update(self) -> None:
        self.rect = pygame.Rect(self.pos, self.size)

    def draw(self) -> None:
        pygame.draw.rect(self.manager.screen, (255, 255, 0), (*(self.pos - self.scene.player.camera.offset), *self.size))
        font_surf = FONT2.render(f"{self.score}", True, (0, 0, 0))
        pos = VEC(self.rect.midtop) - (font_surf.get_width() // 2, font_surf.get_height())
        self.manager.screen.blit(font_surf, pos - self.scene.player.camera.offset)

class OtherSnowball(VisibleSprite):
    def __init__(self, scene: Scene, pos: tuple[int, int]) -> None:
        super().__init__(scene, Layers.SNOWBALL)
        self.pos = VEC(pos)
        self.frame = 0
        self.type = assets.snowball_large
        self.image = self.type[self.frame]
        self.rect = self.image.get_rect(center=self.pos)

    def update(self) -> None:
        self.image = self.type[self.frame]
        self.rect = self.image.get_rect(center=self.pos)

    def draw(self) -> None:
        self.manager.screen.blit(self.image, VEC(self.rect.topleft) - self.scene.player.camera.offset)