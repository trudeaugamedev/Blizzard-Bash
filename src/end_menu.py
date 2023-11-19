from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager

from pygame.locals import SRCALPHA, KEYDOWN, K_RETURN
import pygame

from .constants import WIDTH, HEIGHT, FONT
from .end_menu_score import EndMenuScore
from .scene import Scene

class EndMenu(Scene):
    def __init__(self, manager: GameManager, previous_scene: Scene) -> None:
        super().__init__(manager, previous_scene)
        self.client.running = False

        self.background = pygame.transform.gaussian_blur(self.manager.screen, 15)

        scores = sorted([(player.id, player.name, player.score) for player in self.manager.other_players.values()] + [(self.client.id, self.previous_scene.name, self.previous_scene.score)], key = lambda p: p[1], reverse=True)
        for i, (_id, name, score) in enumerate(scores):
            EndMenuScore(self, i, name, score, self.client.id == _id)

        self.manager.other_players = {}

    def update(self) -> None:
        super().update()
        if KEYDOWN in self.manager.events and self.manager.events[KEYDOWN].key == K_RETURN:
            self.manager.new_scene("StartMenu")

    def draw(self) -> None:
        self.manager.screen.blit(self.background, (0, 0))
        super().draw()