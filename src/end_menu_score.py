from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from .sprite import VisibleSprite, Layers
from .constants import VEC, FONT

from pygame.locals import SRCALPHA
import pytweening as tween
import pygame
import time

class EndMenuScore(VisibleSprite):
    def __init__(self, scene: Scene, index: int, name: str, score: int, mine: bool) -> None:
        super().__init__(scene, Layers.GUI)
        self.pos = VEC(30, 30 + index * 50)
        self.index = index
        self.mine = mine
        self.text = f"{name}: {score}"
        self.text_surf = FONT[36].render(self.text, False, (0, 0, 0))
        self.size = VEC(500, self.text_surf.get_height())
        self.progress = 0
        self.linear_progress = 0
        self.delay_time = time.time()

        if self.mine:
            self.white = False
            self.flash_timer = time.time()
            self.other_text_surf = FONT[36].render(self.text, False, (255, 255, 255))

    def update(self) -> None:
        if time.time() - self.delay_time < 0.4 + self.index * 0.2: return
        self.linear_progress += 0.8 * self.manager.dt
        if self.linear_progress > 1:
            self.linear_progress = 1
            return
        self.progress = tween.easeOutExpo(self.linear_progress)

    def draw(self) -> None:
        if time.time() - self.delay_time < self.index * 0.2: return
        (surf := pygame.Surface(VEC(self.size.x * self.progress, self.size.y), SRCALPHA)).fill((255, 255, 255, 40))
        self.manager.screen.blit(surf, self.pos)
        pygame.draw.rect(self.manager.screen, (0, 0, 0), (self.pos, (self.size.x * self.progress, self.size.y)), 3)
        if self.progress > 0.75:
            self.manager.screen.blit(self.text_surf, self.pos + (12, -5))
            if self.mine:
                if time.time() - self.flash_timer > 0.5:
                    self.flash_timer = time.time()
                    self.white = not self.white
                if self.white:
                    self.manager.screen.blit(self.other_text_surf, self.pos + (12, -5))