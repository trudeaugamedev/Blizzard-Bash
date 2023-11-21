from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from .sprite import VisibleSprite, Layers
from .constants import VEC, FONT, WIDTH

from pygame.locals import SRCALPHA
import pygame

class GameLeaderboard(VisibleSprite):
    def __init__(self, scene: Scene) -> None:
        super().__init__(scene, Layers.GUI)

        self.size = VEC(240, 220)
        self.pos = VEC(WIDTH - self.size.x - 20, 20)

        self.data = []

    def update(self) -> None:
        self.data = [{"name": player.name, "score": player.score} for player in self.manager.other_players.values()]
        self.data.append({"name": self.scene.name, "score": self.scene.score})
        self.data.sort(key = lambda d: d["score"], reverse=True)
        self.size.y = len(self.data) * 26 + 9

    def draw(self) -> None:
        (background := pygame.Surface(self.size, SRCALPHA)).fill((255, 255, 255, 40))
        self.manager.screen.blit(background, self.pos)
        pygame.draw.rect(self.manager.screen, (0, 0, 0), (*self.pos, *self.size), 3)
        pygame.draw.line(self.manager.screen, (0, 0, 0), self.pos + (190, 0), self.pos + (190, self.size.y - 1), 3)
        for i, data in enumerate(self.data):
            text_surf = FONT[20].render(data["name"], True, (0, 0, 0))
            self.manager.screen.blit(text_surf, self.pos + (8, 1 + i * 26))
            text_surf = FONT[20].render(str(data["score"]), True, (0, 0, 0))
            self.manager.screen.blit(text_surf, self.pos + (198, 1 + i * 26))
            if i == len(self.data) - 1: continue
            pygame.draw.line(self.manager.screen, (0, 0, 0), self.pos + (0, 3 + (i + 1) * 26), self.pos + (self.size.x - 1, 3 + (i + 1) * 26), 3)