from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from scene import Scene

from pygame.locals import BLEND_RGB_SUB
from random import choice
from math import sin, pi
import pygame
import time

from .constants import VEC, FONT, PIXEL_SIZE, WIDTH
from .ground import Ground1, Ground2, Ground3
from .sprite import VisibleSprite, Layers
from .swirl import Swirl, VortexSwirl
from .utils import shadow
from .aura import Aura
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
        self.snowballs = {}
        self.rotation = 0
        self.flip = False
        self.score = 0
        self.name = ""
        self.arrow = OtherArrow(self.scene, self)
        self.powerup = -1
        self.powerup_flash_time = time.time()
        self.disconnect_time = time.time()
        self.aura = None

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
        self.image = pygame.transform.rotate(self.upright_image, self.rotation % 360)

        if self.powerup == 3:
            for snowball in self.scene.player.snowballs.values():
                dist = snowball.pos.distance_to(self.pos + VEC(0, -self.size.y / 2))
                if dist <= 250:
                    snowball.time_mult = 0.32
                    snowball.follow = False # don't mess with people's camera if snowball gets stuck

        if time.time() - self.disconnect_time > 1500:
            self.kill()

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
            color = [(63, 134, 165), (233, 86, 86), (88, 210, 103), (204, 102, 255)][self.powerup]
            alpha = (sin((time.time() - self.powerup_flash_time) * pi * 3) * 0.5 + 0.5) * 255
            mask = pygame.mask.from_surface(self.image)
            powerup_overlay = mask.scale(VEC(mask.get_size()) + (20, 14)).to_surface(setcolor=(*color, alpha), unsetcolor=(0, 0, 0, 0))
            self.manager.screen.blit(powerup_overlay, VEC(self.rect.topleft) - (10, 7) - self.scene.player.camera.offset)

        if self.powerup == 3 and self.aura is None:
            self.aura = Aura(self.scene, self)
        elif self.powerup != 3 and self.aura is not None:
            self.aura.kill()
            self.aura = None

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
        if self.aura is not None:
            self.aura.kill()
        # i fucking hate myself
        for snowball in self.snowballs.values():
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
    # Sometimes snowball data can get sent marginally after the snowball is killed, this set is used to prevent that data from being processed
    killed = set()

    def __init__(self, scene: Scene, id: str, pos: tuple[int, int], frame: int, type: int) -> None:
        super().__init__(scene, Layers.SNOWBALL)
        self.id = id
        self.pos = VEC(pos)
        self.frame = frame
        self.type = type
        self.frames = assets.snowball_small if type in {0, 3, 5} else assets.snowball_large
        self.image = self.frames[self.frame]
        self.rect = self.image.get_rect(center=self.pos)
        if self.type == 2:
            self.swirl = Swirl(self.scene, Layers.SNOWBALL, 64)

    def update(self) -> None:
        self.image = self.frames[self.frame]
        self.rect = self.image.get_rect(center=self.pos)
        if self.type == 2:
            self.swirl.pos = self.pos - (32, 32)

    def draw(self) -> None:
        if self.rect.right - self.scene.player.camera.offset.x < -20 or self.rect.left - self.scene.player.camera.offset.x > WIDTH + 20: return
        self.manager.screen.blit(shadow(self.image), VEC(self.rect.topleft) - self.scene.player.camera.offset + (3, 3), special_flags=BLEND_RGB_SUB)
        self.manager.screen.blit(self.image, VEC(self.rect.topleft) - self.scene.player.camera.offset)

    def kill(self) -> None:
        if self.type == 2:
            self.swirl.kill()
            VortexSwirl(self.scene, Layers.SNOWBALL, self.pos - (64, 64), 128, 20, self.id, suck=True)
        __class__.killed.add(self.id)
        super().kill()

class OtherVortex(VisibleSprite):
    instances = {}
    # edge_imgs = [pygame.Surface((32, 32)), pygame.Surface((48, 48)), pygame.Surface((64, 64)), pygame.Surface((80, 80))]
    # for img in edge_imgs:
    #     pygame.draw.circle(img, (2, 2, 2), (img.width // 2, img.height // 2), img.width // 2)

    def __init__(self, scene: Scene, id: str, pos: tuple[int, int], alpha: int) -> None:
        # why tf does this sometimes not get initialized :sob:
        self.image = None
        super().__init__(scene, Layers.STORM)
        self.id = id
        self.pos = VEC(pos) if pos is not None else VEC(0, 0)
        self.alpha = alpha
        self.size = VEC(0, 0)
        # self.blobs = []

    def create_image(self, size: tuple[int, int], offsets: list[tuple[int, int]], radii: list[int]) -> None:
        if self.image is not None: return
        self.size = VEC(size) // PIXEL_SIZE
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        # for offset, radius in zip(offsets, radii):
        #     blob = OtherStormBlob(self.scene, self, offset, radius)
        #     blob.draw()
        #     self.blobs.append(blob)
        # for pos in pygame.mask.from_surface(self.image).outline(3):
        #     img = choice(self.edge_imgs)
        #     self.image.blit(img, VEC(pos) - VEC(img.size) // 2, special_flags=pygame.BLEND_ADD)
        self.image = pygame.transform.scale_by(self.image, PIXEL_SIZE)
        self.image.set_alpha(0)
        self.size *= PIXEL_SIZE

    def update(self) -> None:
        if self.image is None: return
        self.image.set_alpha(self.alpha)

        # if self.id in StormSwirl.instances:
        #     StormSwirl.instances[self.id].storm = self

    def draw(self) -> None:
        if self.image is None: return
        while self.image.get_locked(): pass
        self.manager.screen.blit(self.image, VEC(self.pos) - self.scene.player.camera.offset)

# class OtherStormBlob:
#     def __init__(self, scene: Scene, storm: OtherStorm, offset: tuple[int, int], radius: int) -> None:
#         self.scene = scene
#         self.storm = storm
#         self.offset = VEC(offset)
#         self.radius = radius

#     def draw(self) -> None:
#         pygame.draw.circle(self.storm.image, (138, 155, 178), self.offset, self.radius)
