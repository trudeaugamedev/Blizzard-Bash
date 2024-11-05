from .sprite import VisibleSprite, Layers
from .constants import VEC, WIDTH, HEIGHT
from .button import Button
from .scene import Scene
from . import assets

from random import randint
import pygame

class SkinSelector(VisibleSprite):
    skin_tones = [45, 70, 110, 170, 230]

    def __init__(self, scene: Scene) -> None:
        super().__init__(scene, Layers.GUI)
        self.pos = VEC(WIDTH // 2 + 180, HEIGHT // 2 + 50)
        self.clothes_hue = 128
        self.hat_hue = 0
        self.skin_tone_idx = 2
        self.skin_tone = self.skin_tones[self.skin_tone_idx]
        self.hat_button_left = Button(self.scene, self.pos + (-35, 5), (30, 30), "<", self.prev_hat, style=False, font_size=32, font_color=(0, 0, 0))
        self.skin_button_left = Button(self.scene, self.pos + (-35, 40), (30, 30), "<", self.prev_skin, style=False, font_size=32, font_color=(0, 0, 0))
        self.clothes_button_left = Button(self.scene, self.pos + (-35, 85), (30, 30), "<", self.prev_clothes, style=False, font_size=32, font_color=(0, 0, 0))
        self.hat_button_right = Button(self.scene, self.pos + (110, 5), (30, 30), ">", self.next_hat, style=False, font_size=32, font_color=(0, 0, 0))
        self.skin_button_right = Button(self.scene, self.pos + (110, 40), (30, 30), ">", self.next_skin, style=False, font_size=32, font_color=(0, 0, 0))
        self.clothes_button_right = Button(self.scene, self.pos + (110, 85), (30, 30), ">", self.next_clothes, style=False, font_size=32, font_color=(0, 0, 0))

        for _ in range(randint(0, 7)):
            self.next_hat()

        for _ in range(randint(0, 7)):
            self.next_clothes()

        for _ in range(randint(0, 4)):
            self.next_skin()

    def next_hat(self) -> None:
        self.hat_hue += 32
        self.hat_hue %= 256

    def next_clothes(self) -> None:
        self.clothes_hue += 32
        self.clothes_hue %= 256

    def next_skin(self) -> None:
        self.skin_tone_idx += 1
        self.skin_tone_idx %= len(self.skin_tones)
        self.skin_tone = self.skin_tones[self.skin_tone_idx]

    def prev_hat(self) -> None:
        self.hat_hue -= 32
        self.hat_hue %= 256

    def prev_clothes(self) -> None:
        self.clothes_hue -= 32
        self.clothes_hue %= 256

    def prev_skin(self) -> None:
        self.skin_tone_idx -= 1
        self.skin_tone_idx %= len(self.skin_tones)
        self.skin_tone = self.skin_tones[self.skin_tone_idx]

    def update(self) -> None:
        pass

    def draw(self) -> None:
        self.image = pygame.transform.scale_by(assets.player_idle[0], 2)
        for color in assets.PlayerAssets.clothe_colors:
            self.image = assets.palette_swap(self.image, color, assets.hue_shift(color, self.clothes_hue))
        for color in assets.PlayerAssets.hat_colors:
            self.image = assets.palette_swap(self.image, color, assets.hue_shift(color, self.hat_hue))
        for color in assets.PlayerAssets.skin_colors:
            self.image = assets.palette_swap(self.image, color, assets.lightness_shift(color, self.skin_tone))
        self.manager.screen.blit(self.image, self.pos)
