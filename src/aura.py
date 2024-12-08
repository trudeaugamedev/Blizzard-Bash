from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.player import Player

from src.sprite import VisibleSprite, Layers
from pygame.locals import SRCALPHA
from src.scene import Scene
import pygame
import time

class Aura(VisibleSprite):
    base_img = pygame.Surface((500, 500), SRCALPHA)
    base_img.fill((0, 0, 0, 0))
    for i in range(10):
        pygame.draw.circle(base_img, (204, 102, 255, 15 + i * 12), (250, 250), 250 - i * 25, 26)
    pygame.draw.circle(base_img, (204, 102, 255, 30), (250, 250), 250, 10)

    def __init__(self, scene: Scene, player: Player) -> None:
        super().__init__(scene, Layers.AURA)
        self.player = player
        self.pos = player.pos
        self.image = self.base_img.copy()
        self.rings = []
        self.ring_time = time.time()

    def update(self) -> None:
        self.pos = self.player.pos - (0, self.player.size.y // 2)
        if time.time() - self.ring_time > 0.5:
            self.rings.append(0)
            self.ring_time = time.time()

    def draw(self) -> None:
        self.image = self.base_img.copy()
        for i, rad in enumerate(self.rings):
            if rad > 250:
                self.rings.pop(i)
                continue
            pygame.draw.circle(self.image, (204, 102, 255, 45), (250, 250), rad, int(5 + 10 * (rad / 250)))
            self.rings[i] += 100 * self.manager.dt

        self.scene.manager.screen.blit(self.image, self.pos - self.scene.player.camera.offset - (250, 250))