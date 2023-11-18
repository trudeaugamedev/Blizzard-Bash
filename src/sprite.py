from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from abc import ABC as AbstractClass
from abc import abstractmethod
from enum import Enum, auto

class Layers(Enum):
    PLAYER3 = auto()
    GROUND3 = auto()
    PLAYER2 = auto()
    GROUND2 = auto()
    PLAYER = auto()
    GROUND = auto()
    SNOWBALL = auto()
    SNOWFLAKE = auto()
    POWERUP = auto()
    ARROW = auto()
    GUI = auto()

class Sprite(AbstractClass):
    def __init__(self, scene: Scene, layer: int | Layers) -> None:
        self._layer = Layers(layer)
        self.scene = scene
        self.manager = scene.manager
        self.client = self.manager.client

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def draw(self) -> None:
        pass

    def kill(self) -> None:
        self.scene.sprite_manager.remove(self)

class VisibleSprite(Sprite):
    def __init__(self, scene: Scene, layer: Layers) -> None:
        super().__init__(scene, layer)
        self.scene.sprite_manager.add(self)

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def draw(self) -> None:
        pass

class SpriteManager:
    def __init__(self, scene: Scene) -> None:
        self.scene = scene
        self.manager = scene.manager
        self.layers: dict[Layers, list[Sprite]] = {layer: [] for layer in Layers}

    def update(self) -> None:
        for layer in self.layers:
            for sprite in self.layers[layer]:
                sprite.update()

    def draw(self) -> None:
        for layer in self.layers:
            for sprite in self.layers[layer]:
                sprite.draw()

    def add(self, sprite: Sprite) -> None:
        self.layers[sprite._layer].append(sprite)

    def remove(self, sprite: Sprite) -> None:
        self.layers[sprite._layer].remove(sprite)