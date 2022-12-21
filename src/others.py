from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

import pygame

from .constants import VEC, FONT, PIXEL_SIZE, WIDTH
from .sprite import VisibleSprite, Layers
from . import assets

class OtherPlayer(VisibleSprite):
    def __init__(self, scene: Scene, pos: tuple[int, int]) -> None:
        super().__init__(scene, Layers.PLAYER)
        self.size = VEC(45, 60)
        self.pos = VEC(pos)
        self.frame = 0
        self.orig_image = assets.player[self.frame]
        self.upright_image = self.orig_image
        self.image = self.upright_image
        self.rect = pygame.Rect(self.pos, self.size)
        self.real_rect = self.rect.copy()
        self.real_rect.size = (10 * PIXEL_SIZE, 20 * PIXEL_SIZE)
        self.snowballs = []
        self.rotation = 0
        self.flip = False
        self.score = 0
        self.powerup = None
        self.arrow = OtherArrow(self.scene, self)

    def update(self) -> None:
        self.rect = self.image.get_rect(midbottom=self.pos)
        self.real_rect.midbottom = self.rect.midbottom

        self.orig_image = assets.player[self.frame]
        self.upright_image = pygame.transform.flip(self.orig_image, self.flip, False)
        self.image = pygame.transform.rotate(self.upright_image, self.rotation)

    def draw(self) -> None:
        self.manager.screen.blit(self.image, (*(VEC(self.rect.topleft) - self.scene.player.camera.offset), *self.size))
        text = FONT[28].render(f"{self.score}", True, (0, 0, 0))
        pos = VEC(self.rect.midtop) - (text.get_width() // 2, text.get_height() + 5)
        text_shadow = FONT[28].render(f"{self.score}", True, (0, 0, 0))
        text_shadow.set_alpha(70)
        self.manager.screen.blit(text_shadow, pos + (3, 3) - self.scene.player.camera.offset)
        self.manager.screen.blit(text, pos - self.scene.player.camera.offset)

    def kill(self) -> None:
        self.arrow.kill()
        super().kill()

class OtherArrow(VisibleSprite):
    def __init__(self, scene: Scene, player: OtherPlayer) -> None:
        super().__init__(scene, Layers.ARROW)
        self.player = player

    def update(self) -> None:
        ...

    def draw(self) -> None:
        points = []
        if self.player.rect.right - self.scene.player.camera.offset.x < 0:
            points = [
                VEC(5, self.player.rect.centery - self.scene.player.camera.offset.y),
                VEC(25, self.player.rect.centery - 7 - self.scene.player.camera.offset.y),
                VEC(25, self.player.rect.centery + 7 - self.scene.player.camera.offset.y)
            ]
        elif self.player.rect.left - self.scene.player.camera.offset.x > WIDTH:
            points = [
                VEC(WIDTH - 5, self.player.rect.centery - self.scene.player.camera.offset.y),
                VEC(WIDTH - 25, self.player.rect.centery - 7 - self.scene.player.camera.offset.y),
                VEC(WIDTH - 25, self.player.rect.centery + 7 - self.scene.player.camera.offset.y)
            ]
        if points:
            pygame.draw.polygon(self.manager.screen, (71, 139, 161), points)
            pygame.draw.polygon(self.manager.screen, (0, 0, 0), points, 3)

class OtherSnowball(VisibleSprite):
    def __init__(self, scene: Scene, pos: tuple[int, int], frame: int, sb_type) -> None:
        super().__init__(scene, Layers.SNOWBALL)
        self.pos = VEC(pos)
        self.frame = frame
        self.type = sb_type
        self.image = self.type[self.frame]
        self.rect = self.image.get_rect(center=self.pos)

    def update(self) -> None:
        self.image = self.type[self.frame]
        self.rect = self.image.get_rect(center=self.pos)

    def draw(self) -> None:
        self.manager.screen.blit(self.image, VEC(self.rect.topleft) - self.scene.player.camera.offset)

class OtherPowerup(VisibleSprite):
    def __init__(self, scene: Scene, pos: tuple[int, int]) -> None:
        super().__init__(scene, Layers.POWERUP)
        self.image = assets.powerup_icon
        self.size = VEC(self.image.get_size())
        self.pos = VEC(pos)

    def update(self) -> None:
        ...

    def draw(self) -> None:
        self.manager.screen.blit(self.image, self.pos - self.size // 2 - self.scene.player.camera.offset)