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
        self.client.socket.close()
        for player in self.manager.other_players.values():
            player.kill()
        self.manager.other_players = {}

    def update(self) -> None:
        super().update()

        if KEYDOWN in self.manager.events and self.manager.events[KEYDOWN].key == K_RETURN:
            self.manager.ready = False
            # self.client.thread_data = {}

            self.manager.new_scene("MainGame")

    def draw(self) -> None:
        self.previous_scene.draw()
        super().draw()
        surf = pygame.Surface((WIDTH, HEIGHT), SRCALPHA)
        surf.fill((0, 0, 0, 150))
        self.manager.screen.blit(surf, (0, 0))

        text = FONT[80].render("ELIMINATED!" if self.previous_scene.lost else "You WIN!", True, (255, 191, 0))
        self.manager.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2 - 50))
        text = FONT[40].render("Press Enter to Restart...", True, (255, 191, 0))
        self.manager.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2 + 50))