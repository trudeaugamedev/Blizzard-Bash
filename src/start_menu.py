from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager import GameManager

from .constants import WIDTH, HEIGHT, FONT, TEXT_COLOR
from .skin_selector import SkinSelector
from .input_box import InputBox
from .button import Button
from .scene import Scene
from . import assets

from pygame.locals import SRCALPHA, K_RETURN
import pytweening as tween
import pygame

class StartMenu(Scene):
    def __init__(self, manager: GameManager, previous_scene: Scene) -> None:
        super().__init__(manager, previous_scene)
        self.start_button = Button(self, (WIDTH // 2 - 310, HEIGHT // 2 + 70), (400, 80), "JOIN GAME", self.start_game)
        self.input_box = InputBox(self, (WIDTH // 2 - 105, HEIGHT // 2 - 60), (466, 76))
        self.skin_selector = SkinSelector(self)
        self.warning = ""

        self.title_linear_progress = 0
        self.title_progress = 0
        self.input_linear_progress = -0.3
        self.input_progress = 0
        self.button_linear_progress = -0.5
        self.button_progress = 0

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

        self.client.running = False
        self.manager.new_scene("MainGame")

        self.title_linear_progress += 0.9 * self.manager.dt
        if self.title_linear_progress > 1:
            self.title_linear_progress = 1
        self.title_progress = tween.easeOutBounce(self.title_linear_progress)

        self.input_linear_progress += 0.9 * self.manager.dt
        if self.input_linear_progress > 1:
            self.input_linear_progress = 1
        self.input_progress = tween.easeOutExpo(max(0, self.input_linear_progress))

        self.button_linear_progress += 0.9 * self.manager.dt
        if self.button_linear_progress > 1:
            self.button_linear_progress = 1
        self.button_progress = tween.easeOutBounce(max(0, self.button_linear_progress))
        self.start_button.pos.y = HEIGHT // 2 + 70 + 300 * (1 - self.button_progress)

        if K_RETURN in self.manager.key_downs:
            self.start_game()

    def draw(self) -> None:
        self.manager.window.blit(assets.background, (0, 0))

        self.manager.window.blit(assets.title, (WIDTH // 2 - assets.title.get_width() // 2, HEIGHT // 2 - 240 - 300 * (1 - self.title_progress)))

        (surf := pygame.Surface((748 * self.input_progress, 76), SRCALPHA)).fill((255, 255, 255, 80))
        self.manager.screen.blit(surf, (WIDTH // 2 - 374 * self.input_progress, HEIGHT // 2 - 60))
        pygame.draw.rect(self.manager.screen, (0, 0, 0), (WIDTH // 2 - 374 * self.input_progress, HEIGHT // 2 - 60, 748 * self.input_progress, 76), 3)
        if self.input_progress > 0.9:
            text = FONT[50].render("Username:", False, TEXT_COLOR)
            self.manager.screen.blit(text, (WIDTH // 2 - 359, HEIGHT // 2 - 60))

        text = FONT[24].render(self.warning, False, (255, 0, 0))
        self.manager.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 105))

        super().draw()
