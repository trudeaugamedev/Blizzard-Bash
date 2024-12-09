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

def get_superscript(n: int) -> str:
    if n in {11, 12, 13}: return "th"
    str_n = str(n)
    match str_n[-1]:
        case "1": return "st"
        case "2": return "nd"
        case "3": return "rd"
        case _: return "th"

class EndLeaderboard(VisibleSprite):
    def __init__(self, scene: Scene, index: int, name: str, score: int, mine: bool) -> None:
        super().__init__(scene, Layers.GUI)
        self.pos = VEC(30, 30 + index * 50)
        self.offset2 = 60
        self.offset3 = 410
        self.index = index
        self.mine = mine
        self.rank_surf = FONT[36].render(str(index + 1), False, (0, 0, 0))
        self.rank_ss_surf = FONT[14].render(get_superscript(index + 1), False, (0, 0, 0)) # Superscript
        self.name_surf = FONT[36].render(str(name), False, (0, 0, 0))
        self.score_surf = FONT[36].render(str(score), False, (0, 0, 0))
        self.size = VEC(500, self.rank_surf.get_height())
        self.progress = 0
        self.linear_progress = 0
        self.delay_time = time.time()

        self.surf = pygame.Surface(self.size, SRCALPHA)
        self.surf.fill((255, 255, 255, 40))
        pygame.draw.rect(self.surf, (0, 0, 0), (0, 0, *self.size), 3)
        pygame.draw.line(self.surf, (0, 0, 0), (self.offset2, 0), (self.offset2, self.size.y - 1), 3)
        pygame.draw.line(self.surf, (0, 0, 0), (self.offset3, 0), (self.offset3, self.size.y - 1), 3)
        self.surf.blit(self.rank_surf, (12, -5))
        self.surf.blit(self.name_surf, (self.offset2 + 12, -5))
        self.surf.blit(self.score_surf, (self.offset3 + 12, -5))
        self.surf.blit(self.rank_ss_surf, (12 + self.rank_surf.get_width(), -5 + 8))

        if self.mine:
            self.white = False
            self.flash_timer = time.time()
            self.white_rank_surf = FONT[36].render(str(index + 1), False, (255, 255, 255))
            self.white_rank_ss_surf = FONT[14].render(get_superscript(index + 1), False, (255, 255, 255))
            self.white_name_surf = FONT[36].render(str(name), False, (255, 255, 255))
            self.white_score_surf = FONT[36].render(str(score), False, (255, 255, 255))

    def update(self) -> None:
        if time.time() - self.delay_time < 0.4 + self.index * 0.2: return
        self.linear_progress += 0.8 * self.manager.dt
        if self.progress > 0.99:
            self.progress = 1
        if self.linear_progress > 1:
            self.linear_progress = 1
            return
        self.progress = tween.easeOutExpo(self.linear_progress)

    def draw(self) -> None:
        if time.time() - self.delay_time < self.index * 0.2: return
        self.manager.screen.blit(self.surf, self.pos, (0, 0, self.size.x * self.progress, self.size.y))
        if self.progress > 0.75:
            if self.mine:
                if time.time() - self.flash_timer > 0.5:
                    self.flash_timer = time.time()
                    self.white = not self.white
                if self.white:
                    self.manager.screen.blit(self.white_rank_surf, self.pos + (12, -5))
                    self.manager.screen.blit(self.white_name_surf, self.pos + (self.offset2 + 12, -5))
                    self.manager.screen.blit(self.white_score_surf, self.pos + (self.offset3 + 12, -5))
                    self.manager.screen.blit(self.white_rank_ss_surf, self.pos + (12, -5) + (self.white_rank_surf.get_width(), 8))