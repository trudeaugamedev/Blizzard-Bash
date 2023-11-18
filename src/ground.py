from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from pygame.locals import SRCALPHA, BLEND_RGB_SUB
from math import atan2, degrees
from random import randint
import pygame

from .constants import TILE_SIZE, VEC, PIXEL_SIZE, REAL_TILE_SIZE, WIDTH
from .sprite import VisibleSprite, Layers
from . import assets

class Ground(VisibleSprite):
    instances = {}
    height_map = {}

    def __init__(self, scene: Scene, pos: tuple[int, int], size: tuple[int, int], layer: Layers = Layers.MAP) -> None:
        super().__init__(scene, layer)
        self.size = VEC(size)
        self.pos = VEC(pos)
        self.rect = pygame.Rect(self.pos, self.size)

        self.__class__.instances[int(self.pos.x)] = self

    def generate_unsliced_image(self) -> None:
        self.unsliced_image = pygame.Surface(self.size)
        self.image = pygame.Surface(self.size, SRCALPHA)
        self.unsliced_image.blit(assets.ground_tiles[0].subsurface(randint(0, REAL_TILE_SIZE) * PIXEL_SIZE, 0, TILE_SIZE, TILE_SIZE), (0, 0))
        for i in range(1, int(self.size.y // TILE_SIZE)):
            self.unsliced_image.blit(pygame.transform.flip(assets.ground_tiles[1].subsurface(randint(0, REAL_TILE_SIZE) * PIXEL_SIZE, 0, TILE_SIZE, TILE_SIZE), bool(randint(0, 1)), False), (0, i * TILE_SIZE))

    def apply_gradient(self) -> None:
        self.unsliced_image.blit(assets.gradient, (0, 0), special_flags=BLEND_RGB_SUB)

    def slice_image(self) -> None:
        if self.size.y > 800:
            pygame.draw.rect(self.unsliced_image, (0, 0, 0), (0, 800, TILE_SIZE, 2000))

        try:
            left_height = self.__class__.instances[int(self.pos.x - TILE_SIZE)].pos.y
        except KeyError: # leftmost ground tile
            left_height = self.pos.y
        try:
            right_height = self.__class__.instances[int(self.pos.x + TILE_SIZE)].pos.y
        except KeyError: # rightmost ground tile
            right_height = self.pos.y

        # interval: The height that will be increased for every pixel
        if right_height > self.pos.y and left_height < self.pos.y: # If it's a downwards slope
            interval = right_height - self.pos.y
            y_offset = 0
        elif left_height > self.pos.y and right_height < self.pos.y: # If it's an upwards slope
            interval = self.pos.y - left_height
            y_offset = left_height - self.pos.y
        elif left_height > self.pos.y and right_height > self.pos.y: # If it's at the top of a hill
            interval = right_height - left_height
            y_offset = (max if right_height < left_height else min)(left_height - self.pos.y, right_height - self.pos.y)
        else: # If it's at the bottom of a valley
            interval = 0
            y_offset = 0
        interval /= REAL_TILE_SIZE

        for x in range(REAL_TILE_SIZE): # naming it "surf" instead of "slice" bcs slice is a builtin
            column = self.unsliced_image.subsurface(x * PIXEL_SIZE, 0, PIXEL_SIZE, self.size.y)
            y = x * interval + y_offset
            self.image.blit(column, (x * PIXEL_SIZE, y))
            self.__class__.height_map[int(self.pos.x + x * PIXEL_SIZE)] = self.pos.y + y

        self.incline = degrees(atan2(-interval, PIXEL_SIZE))

    def generate_image(self) -> None:
        self.generate_unsliced_image()
        self.apply_gradient()
        self.slice_image()

    def update(self) -> None:
        ...

    def draw(self) -> None:
        if self.rect.right - self.scene.player.camera.offset.x < 0 or self.rect.left - self.scene.player.camera.offset.x > WIDTH: return
        self.manager.screen.blit(self.image, self.pos - self.scene.player.camera.offset)

class Ground2(Ground):
    instances = {}
    height_map = {}

    def __init__(self, scene: Scene, pos: tuple[int, int], size: tuple[int, int]) -> None:
        super().__init__(scene, pos, size, Layers.MAP2)

    def generate_image(self) -> None:
        self.generate_unsliced_image()
        trans_surf = pygame.Surface(assets.gradient.get_size())
        trans_surf.fill((50, 50, 50))
        gradient = assets.gradient.copy()
        gradient.blit(trans_surf, (0, 0), special_flags=BLEND_RGB_SUB)
        self.unsliced_image.blit(gradient, (0, 0), special_flags=BLEND_RGB_SUB)
        self.slice_image()
        trans_surf = pygame.Surface(self.image.get_size())
        trans_surf.fill((30, 30, 30))
        self.image.blit(trans_surf, (0, 0), special_flags=BLEND_RGB_SUB)

class Ground3(Ground):
    instances = {}
    height_map = {}

    def __init__(self, scene: Scene, pos: tuple[int, int], size: tuple[int, int]) -> None:
        super().__init__(scene, pos, size, Layers.MAP3)

    def generate_image(self) -> None:
        self.generate_unsliced_image()
        trans_surf = pygame.Surface(assets.gradient.get_size())
        trans_surf.fill((50, 50, 50))
        gradient = assets.gradient.copy()
        gradient.blit(trans_surf, (0, 0), special_flags=BLEND_RGB_SUB)
        self.unsliced_image.blit(gradient, (0, 0), special_flags=BLEND_RGB_SUB)
        self.slice_image()
        trans_surf = pygame.Surface(self.image.get_size())
        trans_surf.fill((50, 50, 50))
        self.image.blit(trans_surf, (0, 0), special_flags=BLEND_RGB_SUB)