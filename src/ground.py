from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

import pygame

from .constants import TILE_SIZE, VEC, PIXEL_SIZE, REAL_TILE_SIZE
from .sprite import VisibleSprite, Layers
from . import assets

class Ground(VisibleSprite):
    sorted_instances = {}
    instances = []
    height_map = {}

    def __init__(self, scene: Scene, pos: tuple[int, int], size: tuple[int, int]) -> None:
        super().__init__(scene, Layers.MAP)
        self.size = VEC(size)
        self.pos = VEC(pos)
        self.rect = pygame.Rect(self.pos, self.size)

        self.unsliced_image = pygame.Surface(self.size)
        self.image = self.unsliced_image.copy()
        self.unsliced_image.blit(assets.ground_tiles[0], (0, 0))
        for i in range(1, 11):
            self.unsliced_image.blit(assets.ground_tiles[1], (0, i * TILE_SIZE))
        for x in range(REAL_TILE_SIZE): # naming is "surf" instead of "slice" bcs slice is a builtin
            column = self.unsliced_image.subsurface(x * PIXEL_SIZE, 0, PIXEL_SIZE, self.size.y)
            y = 0 # Do math here
            self.image.blit(column, (x * PIXEL_SIZE, y))
        
        if int(self.pos.y) not in self.__class__.sorted_instances:
            self.__class__.sorted_instances[int(self.pos.y)] = [self]
        else:
            self.__class__.sorted_instances[int(self.pos.y)].append(self)
        self.__class__.instances.append(self)
        self.__class__.height_map[int(self.pos.x)] = self.pos.y

    def update(self) -> None:
        ...

    def draw(self) -> None:
        self.manager.screen.blit(self.image, self.pos - self.scene.player.camera.offset)