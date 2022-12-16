import pygame

from .constants import VEC
from .exe import pathof

def load_img(file: str, factor: float = 3):
    img = pygame.image.load(pathof(file)).convert_alpha()
    return pygame.transform.scale(img, (img.get_width() * factor, img.get_height() * factor))

TEXTURES = "assets/textures"

pygame.display.set_mode()

snowflakes: list[pygame.Surface] = []
for i in range(10):
    snowflakes.append(load_img(f"{TEXTURES}/snowflakes/snowflake_{i}.png", 2))

class Frames:
    def __init__(self, path: str, prefix: str) -> None:
        self.elements = []
        i = 0
        while True:
            try:
                self.elements.append(load_img(f"{TEXTURES}/{path}/{prefix}{i}.png"))
            except FileNotFoundError:
                break
            i += 1
        self.length = len(self.elements)
        self.size = VEC(self[0].get_size())

    def __getitem__(self, i) -> pygame.Surface:
        return self.elements[i]

snowball_large = Frames("snowballs", "snowball_large_")
snowball_small = Frames("snowballs", "snowball_small_")

pygame.display.quit()
