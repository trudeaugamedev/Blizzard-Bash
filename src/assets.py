import pygame

from .constants import VEC, PIXEL_SIZE
from .exe import pathof

def load_img(file: str, factor: float = PIXEL_SIZE, alpha: bool = True):
    if alpha:
        img = pygame.image.load(pathof(file)).convert_alpha()
    else:
        img = pygame.image.load(pathof(file)).convert()
    return pygame.transform.scale(img, (img.get_width() * factor, img.get_height() * factor))

TEXTURES = "assets/textures"

pygame.display.set_mode()

snowflakes: list[pygame.Surface] = []
for i in range(10):
    snowflakes.append(load_img(f"{TEXTURES}/snowflake/snowflake_{i}.png", 2))

ground_tiles: list[pygame.Surface] = [
    load_img(f"{TEXTURES}/ground/ground_0.png", alpha=False),
    load_img(f"{TEXTURES}/ground/ground_1.png", alpha=False)
]

powerup_icon = load_img(f"{TEXTURES}/misc/icon_rapidfire.png", alpha=False)

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

player_idle = Frames("player", "player_idle_")
player_dig = Frames("player", "player_dig_")
player = player_idle.elements + player_dig.elements

snowball_large = Frames("snowball", "snowball_large_")
snowball_small = Frames("snowball", "snowball_small_")

pygame.display.quit()
