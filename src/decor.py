from .sprite import VisibleSprite, Layers
from .constants import VEC, WIDTH
from .utils import shadow
from .scene import Scene
from . import assets

from pygame.locals import BLEND_RGB_SUB
from random import choices, randint
import pygame

class Tree(VisibleSprite):
    def __init__(self, scene: Scene, pos: tuple[int, int], angle: int, layer: Layers) -> None:
        super().__init__(scene, layer)
        self.pos = VEC(pos)
        self.image = choices(assets.trees, assets.tree_weights)[0]
        self.image = pygame.transform.flip(self.image, randint(0, 1), False)
        self.image = pygame.transform.rotate(self.image, angle * 0.5)
        self.shadow_image = shadow(self.image)
        self.size = VEC(self.image.get_size())
        self.pos.y += abs(angle) * 0.8 + 9

    def update(self) -> None:
        ...

    def draw(self) -> None:
        if self.pos.x < self.scene.player.camera.offset.x - 100 or self.pos.x > self.scene.player.camera.offset.x + WIDTH + 100: return
        self.manager.screen.blit(self.shadow_image, self.pos - (self.size.x // 2, self.size.y) - self.scene.player.camera.offset + (3, 3), special_flags=BLEND_RGB_SUB)
        self.manager.screen.blit(self.image, self.pos - (self.size.x // 2, self.size.y) - self.scene.player.camera.offset)

class Rock(VisibleSprite):
    def __init__(self, scene: Scene, pos: tuple[int, int], angle: int, layer: Layers) -> None:
        super().__init__(scene, layer)
        self.pos = VEC(pos)
        self.image = choices(assets.rocks, assets.rock_weights)[0]
        self.image = pygame.transform.flip(self.image, randint(0, 1), False)
        self.image = pygame.transform.rotate(self.image, angle)
        self.shadow_image = shadow(self.image)
        self.size = VEC(self.image.get_size())
        self.pos.y += abs(angle) * 0.65 + 7

    def update(self) -> None:
        ...

    def draw(self) -> None:
        if self.pos.x < self.scene.player.camera.offset.x - 30 or self.pos.x > self.scene.player.camera.offset.x + WIDTH + 30: return
        self.manager.screen.blit(self.shadow_image, self.pos - (self.size.x // 2, self.size.y) - self.scene.player.camera.offset + (3, 3), special_flags=BLEND_RGB_SUB)
        self.manager.screen.blit(self.image, self.pos - (self.size.x // 2, self.size.y) - self.scene.player.camera.offset, )