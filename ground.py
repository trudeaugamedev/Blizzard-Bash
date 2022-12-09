from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

import pygame

from sprite import VisibleSprite, Layers
from constants import VEC

# Test blocks for reference, to actually be able to see the player moving
class Ground(VisibleSprite):
    sorted_instances = {}
    instances = []
    height_map = {}

    def __init__(self, scene: Scene, pos: tuple[int, int], size: tuple[int, int]) -> None:
        super().__init__(scene, Layers.PLAYER)
        self.size = VEC(size)
        self.pos = VEC(pos)
        self.rect = pygame.Rect(self.pos, self.size)

        if int(self.pos.y) not in self.__class__.sorted_instances:
            self.__class__.sorted_instances[int(self.pos.y)] = [self]
        else:
            self.__class__.sorted_instances[int(self.pos.y)].append(self)
        self.__class__.instances.append(self)
        self.__class__.height_map[int(self.pos.x)] = self.pos.y

    def update(self) -> None:
        ...

    def draw(self) -> None:
        pygame.draw.rect(self.manager.screen, (0, 0, 0), (*(self.pos - self.scene.player.camera.offset), *self.size))