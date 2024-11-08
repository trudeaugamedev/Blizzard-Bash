from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from pygame.locals import BLEND_RGB_SUB
from math import sin, pi
import pygame
import time

from .constants import VEC, FONT, PIXEL_SIZE, WIDTH
from .ground import Ground1, Ground2, Ground3
from .sprite import VisibleSprite, Layers
from .utils import shadow
from . import assets

class OtherPlayer(VisibleSprite):
    def __init__(self, scene: Scene, _id: int, pos: tuple[int, int]) -> None:
        super().__init__(scene, Layers.PLAYER1)
        self.id = _id
        self.size = VEC(45, 60)
        self.pos = VEC(pos)
        self.frame = 0
        self.clothes_hue = 135
        self.hat_hue = 0
        self.skin_tone = 230
        self.assets = assets
        self.orig_image = self.assets.player[self.frame]
        self.upright_image = self.orig_image
        self.image = self.upright_image
        self.rect = pygame.Rect(self.pos, self.size)
        self.real_rect = self.rect.copy()
        self.real_rect.size = (10 * PIXEL_SIZE, 20 * PIXEL_SIZE)
        self.snowballs = []
        self.rotation = 0
        self.flip = False
        self.score = 0
        self.name = ""
        self.arrow = OtherArrow(self.scene, self)
        self.powerup = -1
        self.powerup_flash_time = time.time()

    def update(self) -> None:
        self.rect = self.image.get_rect(midbottom=self.pos)
        self.real_rect.midbottom = self.rect.midbottom

        centerx = int(self.rect.centerx // PIXEL_SIZE * PIXEL_SIZE)
        y1 = Ground1.height_map[centerx]
        y2 = Ground2.height_map[centerx]
        y3 = Ground3.height_map[centerx]
        if self.pos.y < y3 + 12 and y2 > y3 and self._layer != Layers.PLAYER3:
            self.scene.sprite_manager.remove(self)
            self._layer = Layers.PLAYER3
            self.scene.sprite_manager.add(self)
        elif y3 + 12 < self.pos.y < y2 + 12 and self._layer != Layers.PLAYER2:
            self.scene.sprite_manager.remove(self)
            self._layer = Layers.PLAYER2
            self.scene.sprite_manager.add(self)
        elif y2 + 12 < self.pos.y < y1 + 12 and self._layer != Layers.PLAYER1:
            self.scene.sprite_manager.remove(self)
            self._layer = Layers.PLAYER1
            self.scene.sprite_manager.add(self)

        self.orig_image = self.assets.player[self.frame]
        self.upright_image = pygame.transform.flip(self.orig_image, self.flip, False)
        self.image = pygame.transform.rotate(self.upright_image, self.rotation)

    def set_colors(self, clothes, hat, skin):
        if clothes == self.clothes_hue and hat == self.hat_hue and skin == self.skin_tone: return
        self.clothes_hue = clothes
        self.hat_hue = hat
        self.skin_tone = skin
        self.assets = assets.PlayerAssets(clothes, hat, skin)

    def draw(self) -> None:
        if self.rect.right - self.scene.player.camera.offset.x < -20 or self.rect.left - self.scene.player.camera.offset.x > WIDTH + 20: return

        self.manager.screen.blit(shadow(self.image), VEC(self.rect.topleft) - self.scene.player.camera.offset + (3, 3), special_flags=BLEND_RGB_SUB)

        if self.powerup != -1:
            color = [(63, 134, 165), (233, 86, 86), (78, 180, 93)][self.powerup]
            alpha = (sin((time.time() - self.powerup_flash_time) * pi * 3) * 0.5 + 0.5) * 255
            mask = pygame.mask.from_surface(self.image)
            powerup_overlay = mask.scale(VEC(mask.get_size()) + (20, 14)).to_surface(setcolor=(*color, alpha), unsetcolor=(0, 0, 0, 0))
            self.manager.screen.blit(powerup_overlay, VEC(self.rect.topleft) - (10, 7) - self.scene.player.camera.offset)

        self.manager.screen.blit(self.image, VEC(self.rect.topleft) - self.scene.player.camera.offset)

        if self.powerup != -1:
            powerup_overlay.set_alpha(100)
            self.manager.screen.blit(powerup_overlay, VEC(self.rect.topleft) - (10, 7) - self.scene.player.camera.offset)

        text = FONT[28].render(f"{self.score}", False, (0, 0, 0))
        pos = VEC(self.rect.midtop) - (text.get_width() // 2, text.get_height() + 5)
        text_shadow = FONT[28].render(f"{self.score}", False, (0, 0, 0))
        text_shadow.set_alpha(70)
        self.manager.screen.blit(text_shadow, pos + (3, 3) - self.scene.player.camera.offset)
        self.manager.screen.blit(text, pos - self.scene.player.camera.offset)

        text = FONT[20].render(f"{self.name}", False, (0, 0, 0))
        pos = VEC(self.rect.midtop) - (text.get_width() // 2, text.get_height() + 40)
        text_shadow = FONT[20].render(f"{self.name}", False, (0, 0, 0))
        text_shadow.set_alpha(70)
        self.manager.screen.blit(text_shadow, pos + (3, 3) - self.scene.player.camera.offset)
        self.manager.screen.blit(text, pos - self.scene.player.camera.offset)

    def kill(self) -> None:
        self.arrow.kill()
        for snowball in self.snowballs:
            snowball.kill()
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
    def __init__(self, scene: Scene, pos: tuple[int, int], frame: int, _type: int) -> None:
        super().__init__(scene, Layers.SNOWBALL)
        self.pos = VEC(pos)
        self.frame = frame
        self.type = assets.snowball_large if _type else assets.snowball_small
        self.image = self.type[self.frame]
        self.rect = self.image.get_rect(center=self.pos)

    def update(self) -> None:
        self.image = self.type[self.frame]
        self.rect = self.image.get_rect(center=self.pos)

    def draw(self) -> None:
        if self.rect.right - self.scene.player.camera.offset.x < -20 or self.rect.left - self.scene.player.camera.offset.x > WIDTH + 20: return
        self.manager.screen.blit(shadow(self.image), VEC(self.rect.topleft) - self.scene.player.camera.offset + (3, 3), special_flags=BLEND_RGB_SUB)
        self.manager.screen.blit(self.image, VEC(self.rect.topleft) - self.scene.player.camera.offset)