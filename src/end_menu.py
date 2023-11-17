from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager

from pygame.locals import SRCALPHA, KEYDOWN, K_RETURN
import pygame

from .constants import WIDTH, HEIGHT, FONT
from .scene import Scene

class EndMenu(Scene):
    def __init__(self, manager: GameManager, previous_scene: Scene) -> None:
        super().__init__(manager, previous_scene)
        self.client.running = False
        self.manager.other_players = {}

        self.background = pygame.transform.gaussian_blur(self.manager.screen, 15)

    def update(self) -> None:
        super().update()
        if KEYDOWN in self.manager.events and self.manager.events[KEYDOWN].key == K_RETURN:
            self.manager.new_scene("StartMenu")

    def draw(self) -> None:
        self.manager.screen.blit(self.background, (0, 0))
        super().draw()