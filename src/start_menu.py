from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager

from .constants import WIDTH, HEIGHT, FONT, TEXT_COLOR
from .input_box import InputBox
from .button import Button
from .scene import Scene
from . import assets

import pygame

class StartMenu(Scene):
    def __init__(self, manager: GameManager, previous_scene: Scene) -> None:
        super().__init__(manager, previous_scene)
        self.start_button = Button(
            self, (WIDTH // 2, HEIGHT // 2 + 70), (300, 80), "JOIN GAME",
            lambda: self.manager.new_scene("MainGame"), centered=True
        )
        self.input_box = InputBox(self, (WIDTH // 2 - 109, HEIGHT // 2 - 70), (466, 76))

    def update(self) -> None:
        super().update()

    def draw(self) -> None:
        self.manager.screen.blit(assets.background, (0, 0))
        pygame.draw.rect(self.manager.screen, (196, 230, 255), (WIDTH // 2 - 374, HEIGHT // 2 - 70, 400, 76))
        text = FONT[50].render("Username:", True, TEXT_COLOR)
        self.manager.screen.blit(text, (WIDTH // 2 - 359, HEIGHT // 2 - 70))
        super().draw()