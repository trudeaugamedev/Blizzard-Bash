from colorsys import rgb_to_hsv, hsv_to_rgb
from copy import copy
import pygame

from .constants import VEC, PIXEL_SIZE, TILE_SIZE
from .utils import clamp
from .exe import pathof

def load_img(file: str, factor: float = PIXEL_SIZE, alpha: bool = True):
    if alpha:
        img = pygame.image.load(pathof(file)).convert_alpha()
    else:
        img = pygame.image.load(pathof(file)).convert()
    return pygame.transform.scale(img, (img.get_width() * factor, img.get_height() * factor))

def hue_shift(color, hue):
    hsv = list(rgb_to_hsv(color[0] / 255, color[1] / 255, color[2] / 255))
    hsv[0] = hue / 255
    rgb = hsv_to_rgb(hsv[0], hsv[1], hsv[2])
    rgb = (rgb[0] * 255, rgb[1] * 255, rgb[2] * 255)
    return rgb

f_r = lambda x: -0.004509 * x ** 2 + 2.130 * x - 4.847
f_g = lambda x: -0.003080 * x ** 2 + 1.822 * x - 33.08
f_b = lambda x: 0.8975 * x - 5.025
def lightness_shift(color, lightness):
    shade = 0.9 if color == PlayerAssets.skin_colors[0] else 1
    rgb = (clamp(f_r(lightness) * shade, 0, 255)[0], clamp(f_g(lightness) * shade, 0, 255)[0], clamp(f_b(lightness) * shade, 0, 255)[0])
    return rgb

def palette_swap(surf, old, new):
    copy = surf.copy()
    pygame.transform.threshold(copy, surf, old, (0, 0, 0), new, 1, None, True)
    return copy

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
crosshair = load_img(f"{TEXTURES}/misc/crosshair.png", alpha=True)

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

def palette_swap_frames(frames, old, new):
    for i in range(frames.length):
        frames.elements[i] = palette_swap(frames[i], old, new)

def deepcopy(frames):
    frames_copy = copy(frames)
    frames_copy.elements = []
    for i in range(frames.length):
        frames_copy.elements.append(frames[i].copy())
    return frames_copy

class PlayerAssets:
    clothe_colors = [
        (22, 107, 135),
        (100, 166, 188),
        (133, 188, 206),
        (165, 216, 232),
        (71, 139, 161),
        (22, 107, 135),
        (2, 35, 45),
    ]
    hat_colors = [
        (86, 4, 4),
        (184, 52, 52),
        (240, 233, 233),
        (191, 169, 169),
        (236, 224, 224),
        (244, 244, 244),
        (218, 199, 199),
        (233, 223, 223),
    ]
    skin_colors = [
        (221, 193, 180),
        (255, 235, 226),
    ]

    def __init__(self, clothes_hue: int, hat_hue: int, skin_tone: int) -> None:
        self.clothes_hue = clothes_hue
        self.hat_hue = hat_hue
        self.skin_tone = skin_tone

        self.player_idle = deepcopy(player_idle)
        self.player_idle_l = deepcopy(player_idle_l)
        self.player_idle_s = deepcopy(player_idle_s)
        self.player_dig = deepcopy(player_dig)
        self.player_run = deepcopy(player_run)
        self.player_run_s = deepcopy(player_run_s)
        self.player_run_l = deepcopy(player_run_l)
        self.player_throw_l = deepcopy(player_throw_l)
        self.player_throw_s = deepcopy(player_throw_s)
        self.frames_objects = [self.player_idle, self.player_idle_l, self.player_idle_s, self.player_dig, self.player_run, self.player_run_s, self.player_run_l, self.player_throw_l, self.player_throw_s]
        for frames in self.frames_objects:
            for color in self.clothe_colors:
                palette_swap_frames(frames, color, hue_shift(color, self.clothes_hue))
            for color in self.hat_colors:
                palette_swap_frames(frames, color, hue_shift(color, self.hat_hue))
            for color in self.skin_colors:
                palette_swap_frames(frames, color, lightness_shift(color, self.skin_tone))
        self.player = self.player_idle.elements + self.player_idle_l.elements + self.player_idle_s.elements + self.player_dig.elements + self.player_run.elements + self.player_run_s.elements + self.player_run_l.elements + self.player_throw_l.elements + self.player_throw_s.elements

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

pygame.mixer.pre_init(buffer=32)
pygame.mixer.init(buffer=32)

hit_sounds = [
    pygame.mixer.Sound(pathof("assets/audio/hit1.wav")),
    pygame.mixer.Sound(pathof("assets/audio/hit2.wav")),
    pygame.mixer.Sound(pathof("assets/audio/hit3.wav")),
    pygame.mixer.Sound(pathof("assets/audio/hit4.wav")),
]
throw_sound = pygame.mixer.Sound(pathof("assets/audio/throw.wav"))