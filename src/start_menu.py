from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager

from .constants import WIDTH, HEIGHT, FONT, TEXT_COLOR
from .input_box import InputBox
from .button import Button
from .scene import Scene
from . import assets

from pygame.locals import SRCALPHA
import pygame

class StartMenu(Scene):
    def __init__(self, manager: GameManager, previous_scene: Scene) -> None:
        super().__init__(manager, previous_scene)
        self.start_button = Button(self, (WIDTH // 2, HEIGHT // 2 + 120), (300, 80), "JOIN GAME", self.start_game, centered=True)
        self.input_box = InputBox(self, (WIDTH // 2 - 105, HEIGHT // 2 - 20), (466, 76))
        self.warning = ""

    def start_game(self) -> None:
        text = self.input_box.text
        if not text:
            self.warning = "Please enter a username!"
            return
        text = text.strip()
        if not text:
            self.warning = "The username must not only contain spaces!"
            return
        self.input_box.text = text
        self.manager.new_scene("MainGame")

    def update(self) -> None:
        super().update()

    def draw(self) -> None:
        self.manager.screen.blit(assets.background, (0, 0))

        self.manager.screen.blit(assets.title, (WIDTH // 2 - assets.title.get_width() // 2, HEIGHT // 2 - 200))

        (surf := pygame.Surface((748, 76), SRCALPHA)).fill((255, 255, 255, 80))
        self.manager.screen.blit(surf, (WIDTH // 2 - 374, HEIGHT // 2 - 20))
        pygame.draw.rect(self.manager.screen, (0, 0, 0), (WIDTH // 2 - 374, HEIGHT // 2 - 20, 748, 76), 3)
        text = FONT[50].render("Username:", False, TEXT_COLOR)
        self.manager.screen.blit(text, (WIDTH // 2 - 359, HEIGHT // 2 - 20))

        text = FONT[24].render(self.warning, False, (255, 0, 0))
        self.manager.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 65))

        super().draw()