from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager

from pygame.locals import KEYDOWN, K_RETURN
import pygame

from .end_leaderboard import EndLeaderboard
from .constants import WIDTH, HEIGHT
from .button import Button
from .scene import Scene

class EndMenu(Scene):
    def __init__(self, manager: GameManager, previous_scene: Scene) -> None:
        super().__init__(manager, previous_scene)
        self.client.running = False

        self.background = pygame.transform.gaussian_blur(self.manager.screen, 15)

        scores = sorted(self.previous_scene.score_data, key = lambda d: d["score"] if "score" in d else -1, reverse=True)
        for i, data in enumerate(scores):
            if "score" not in data: continue
            EndLeaderboard(self, i, data["name"], data["score"], self.client.id == data["id"])

        self.manager.other_players = {}

        self.button = Button(self, (WIDTH - 300 - 30, HEIGHT - 80 - 30), (300, 80), "Back", lambda: self.manager.new_scene("StartMenu"))

    def update(self) -> None:
        super().update()

    def draw(self) -> None:
        self.manager.screen.blit(self.background, (0, 0))
        super().draw()