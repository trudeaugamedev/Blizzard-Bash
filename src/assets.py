import pygame

from .constants import VEC, PIXEL_SIZE, TILE_SIZE
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
    snowflakes.append(load_img(f"{TEXTURES}/snowflake/snowflake_{i}.png", 2, alpha=False))
    snowflakes[i].set_colorkey((0, 0, 0))

ground_tiles: list[pygame.Surface] = [
    load_img(f"{TEXTURES}/ground/ground.png", alpha=False).subsurface(0, 0, TILE_SIZE * 2, TILE_SIZE),
    load_img(f"{TEXTURES}/ground/ground.png", alpha=False).subsurface(0, TILE_SIZE, TILE_SIZE * 2, TILE_SIZE),
]

trees = [
    load_img(f"{TEXTURES}/decor/tree1.png", alpha=True),
    load_img(f"{TEXTURES}/decor/tree2.png", alpha=True),
]
tree_weights = [
    2,
    3,
]
rocks = [
    load_img(f"{TEXTURES}/decor/rock1.png", alpha=True),
    load_img(f"{TEXTURES}/decor/rock2.png", alpha=True),
]
rock_weights = [
    8,
    5,
]

powerup_icons = {
    "rapidfire": load_img(f"{TEXTURES}/powerup/rapidfire.png", alpha=False),
    "strength": load_img(f"{TEXTURES}/powerup/strength.png", alpha=False),
    "clustershot": load_img(f"{TEXTURES}/powerup/clustershot.png", alpha=False),
}
gradient = pygame.transform.scale((load_img(f"{TEXTURES}/misc/gradient.png", factor=1)), (TILE_SIZE, 800))
background = load_img(f"{TEXTURES}/misc/background.png", alpha=False)
title = load_img(f"{TEXTURES}/misc/title.png", alpha=True)
border = load_img(f"{TEXTURES}/misc/border.png", alpha=True)
frost_vignette = load_img(f"{TEXTURES}/vignette/frost_vignette.png", alpha=True)
elim_vignette = load_img(f"{TEXTURES}/vignette/elim_vignette.png", alpha=True)

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
player_idle_l = Frames("player", "player_idle_l_")
player_idle_s = Frames("player", "player_idle_s_")
player_dig = Frames("player", "player_dig_")
player_run = Frames("player", "player_run_")
player_run_s = Frames("player", "player_run_s_")
player_run_l = Frames("player", "player_run_l_")
player_throw_l = Frames("player", "player_throw_l_")
player_throw_s = Frames("player", "player_throw_s_")
player = player_idle.elements + player_idle_l.elements + player_idle_s.elements + player_dig.elements + player_run.elements + player_run_s.elements + player_run_l.elements + player_throw_l.elements + player_throw_s.elements

snowball_large = Frames("snowball", "snowball_large_")
snowball_small = Frames("snowball", "snowball_small_")

pygame.display.quit()

pygame.mixer.init()

hit_sounds = [
    pygame.mixer.Sound("assets/audio/hit1.wav"),
    pygame.mixer.Sound("assets/audio/hit2.wav"),
    pygame.mixer.Sound("assets/audio/hit3.wav"),
    pygame.mixer.Sound("assets/audio/hit4.wav"),
]