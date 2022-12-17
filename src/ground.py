from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from pygame.locals import SRCALPHA
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
        
        if int(self.pos.y) not in self.__class__.sorted_instances:
            self.__class__.sorted_instances[int(self.pos.y)] = [self]
        else:
            self.__class__.sorted_instances[int(self.pos.y)].append(self)
        self.__class__.instances.append(self)
        self.__class__.height_map[int(self.pos.x)] = self.pos.y

    def generate_image(self) -> None:
        self.unsliced_image = pygame.Surface(self.size)
        self.image = pygame.Surface(self.size, SRCALPHA)
        self.unsliced_image.blit(assets.ground_tiles[0], (0, 0))
        for i in range(1, 11):
            self.unsliced_image.blit(assets.ground_tiles[1], (0, i * TILE_SIZE))

        try:
            left_height = self.__class__.height_map[int(self.pos.x - TILE_SIZE)]
        except KeyError: # leftmost ground tile
            left_height = self.pos.y
        try:
            right_height = self.__class__.height_map[int(self.pos.x + TILE_SIZE)]
        except KeyError: # rightmost ground tile
            right_height = self.pos.y

        # interval: The height that will be increased for every pixel
        if right_height > self.pos.y and left_height < self.pos.y: # If it's a downwards slope
            interval = right_height - self.pos.y
            y_offset = 0
        elif left_height > self.pos.y and right_height < self.pos.y: # If it's an upwards slope
            interval = self.pos.y - left_height
            y_offset = left_height - self.pos.y
        else: # If it's at the top or bottom of a hill
            interval = right_height - left_height
            y_offset = (max if right_height < left_height else min)(left_height - self.pos.y, right_height - self.pos.y)
        interval /= REAL_TILE_SIZE

        for x in range(REAL_TILE_SIZE): # naming it "surf" instead of "slice" bcs slice is a builtin
            column = self.unsliced_image.subsurface(x * PIXEL_SIZE, 0, PIXEL_SIZE, self.size.y)
            y = x * interval + y_offset
            self.image.blit(column, (x * PIXEL_SIZE, y))
            
        self.rect.y += abs(self.pos.y - left_height) * 1.5

    def update(self) -> None:
        ...

    def draw(self) -> None:
        self.manager.screen.blit(self.image, self.pos - self.scene.player.camera.offset)