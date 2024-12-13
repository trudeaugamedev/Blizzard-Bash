from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from pygame.locals import SRCALPHA, BLEND_RGB_SUB
from random import randint, choice, choices
from math import atan2, degrees, sqrt
import opensimplex as noise
import pygame

from .constants import TILE_SIZE, VEC, PIXEL_SIZE, REAL_TILE_SIZE, WIDTH
from .sprite import Sprite, VisibleSprite, Layers
from .decor import Tree, Rock
from .utils import sign
from . import assets

class Ground1Manager(VisibleSprite):
    def __init__(self, scene: Scene, ground: Ground1 | Ground2 | Ground3 = None, layer: Layers = Layers.GROUND1) -> None:
        super().__init__(scene, layer)
        self.ground = ground if ground else Ground1
        self.size = VEC(26 * TILE_SIZE, 720)
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey((0, 0, 0))
        self.pos = VEC(-WIDTH // 2, -450)
        self.tile_x = self.pos.x // TILE_SIZE
        self.create_ground()

    def create_ground(self) -> None:
        for x in range(-110, 110):
            # Horizontal stretch and vertical stretch (essentially)
            y = noise.noise2(x * 0.1, 0) * 150
            ground = Ground1(self.scene, self, (x * TILE_SIZE, y), (TILE_SIZE, 400 - y))
        for ground in Ground1.instances.values():
            ground.generate_image() # Create a images only after all tiles have been created
            ground.draw()
        for _ in range(30):
            ground = choice(list(self.ground.instances.values()))
            (choices([Tree, Rock], [1, 3])[0])(self.scene, ground.pos + (TILE_SIZE // 2, 0), ground.incline, choice([Layers.DECOR1, Layers.DECOR2]))

    def update(self) -> None:
        if self.scene.player.camera.offset.x < self.pos.x:
            self.pos.x -= TILE_SIZE
            self.tile_x = self.pos.x // TILE_SIZE
            self.shift_image_left()
        elif self.scene.player.camera.offset.x + WIDTH > self.pos.x + self.size.x:
            self.pos.x += TILE_SIZE
            self.tile_x = self.pos.x // TILE_SIZE
            self.shift_image_right()

    def shift_image_left(self) -> None:
        new_image = pygame.Surface(self.size)
        new_image.set_colorkey((0, 0, 0))
        new_image.blit(self.image, (TILE_SIZE, 0))
        self.image = new_image
        self.ground.instances[int(self.tile_x * TILE_SIZE)].draw()
        self.ground.instances[int(self.tile_x * TILE_SIZE + TILE_SIZE)].draw()

    def shift_image_right(self) -> None:
        new_image = pygame.Surface(self.size)
        new_image.set_colorkey((0, 0, 0))
        new_image.blit(self.image, (-TILE_SIZE, 0))
        self.image = new_image
        self.ground.instances[int(self.tile_x * TILE_SIZE + self.size.x)].draw()
        self.ground.instances[int(self.tile_x * TILE_SIZE - TILE_SIZE + self.size.x)].draw()

    def draw(self) -> None:
        self.manager.screen.fblits([(self.image, self.pos - self.scene.player.camera.offset)])

class Ground2Manager(Ground1Manager):
    def __init__(self, scene: Scene) -> None:
        super().__init__(scene, Ground2, Layers.GROUND2)
        self.ground = Ground2

    def create_ground(self) -> None:
        for x in range(-110, 110):
            # Horizontal stretch and vertical stretch (essentially)
            y = noise.noise2(x * 0.1 + 10000, 0) * 200 - 120
            Ground2(self.scene, self, (x * TILE_SIZE, y), (TILE_SIZE, 330 - y))
        for ground in Ground2.instances.values():
            ground.generate_image() # Create a images only after all tiles have been created
            ground.draw()
        for _ in range(25):
            ground = choice(list(self.ground.instances.values()))
            (choices([Tree, Rock], [1, 3])[0])(self.scene, ground.pos + (TILE_SIZE // 2, 0), ground.incline, choice([Layers.DECOR3, Layers.DECOR4]))

class Ground3Manager(Ground1Manager):
    def __init__(self, scene: Scene) -> None:
        super().__init__(scene, Ground3, Layers.GROUND3)
        self.ground = Ground3

    def create_ground(self) -> None:
        for x in range(-110, 110):
            # Horizontal stretch and vertical stretch (essentially)
            y = noise.noise2(x * 0.1 + 20000, 0) * 250 - 250
            Ground3(self.scene, self, (x * TILE_SIZE, y), (TILE_SIZE, 330 - y))
        for ground in Ground3.instances.values():
            ground.generate_image() # Create a images only after all tiles have been created
            ground.draw()
        for _ in range(20):
            ground = choice(list(self.ground.instances.values()))
            (choices([Tree, Rock], [1, 3])[0])(self.scene, ground.pos + (TILE_SIZE // 2, 0), ground.incline, choice([Layers.DECOR5, Layers.DECOR6]))

class Ground1(Sprite):
    instances = {}
    height_map = {}

    def __init__(self, scene: Scene, ground_manager: Ground1Manager, pos: tuple[int, int], size: tuple[int, int], layer: Layers = Layers.GROUND1) -> None:
        super().__init__(scene, layer)
        self.ground_manager = ground_manager
        self.size = VEC(size)
        self.pos = VEC(pos)
        self.rect = pygame.Rect(self.pos, self.size)

        self.__class__.instances[int(self.pos.x)] = self

    def generate_unsliced_image(self) -> None:
        self.unsliced_image = pygame.Surface(self.size)
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey((0, 0, 0))
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

        for x in range(REAL_TILE_SIZE):
            column = self.unsliced_image.subsurface(x * PIXEL_SIZE, 0, PIXEL_SIZE, self.size.y)
            y = (x * interval + y_offset)
            self.image.blit(column, (x * PIXEL_SIZE, y // PIXEL_SIZE * PIXEL_SIZE))
            self.__class__.height_map[int(self.pos.x + x * PIXEL_SIZE)] = self.pos.y + y

        self.incline = degrees(atan2(-interval, PIXEL_SIZE))

    def generate_image(self) -> None:
        self.generate_unsliced_image()
        self.apply_gradient()
        self.slice_image()

    def update(self) -> None:
        ...

    def draw(self) -> None:
        self.ground_manager.image.blit(self.image, self.pos - self.ground_manager.pos)

class Ground2(Ground1):
    instances = {}
    height_map = {}

    def __init__(self, scene: Scene, ground_manager: Ground1Manager, pos: tuple[int, int], size: tuple[int, int]) -> None:
        super().__init__(scene, ground_manager, pos, size, Layers.GROUND2)

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

class Ground3(Ground1):
    instances = {}
    height_map = {}

    def __init__(self, scene: Scene, ground_manager: Ground1Manager, pos: tuple[int, int], size: tuple[int, int]) -> None:
        super().__init__(scene, ground_manager, pos, size, Layers.GROUND3)

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