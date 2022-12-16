import pygame

from .exe import pathof

def load_img(file: str, factor: float = 4):
    img = pygame.image.load(pathof(file)).convert_alpha()
    return pygame.transform.scale(img, (img.get_width() * factor, img.get_height() * factor))

pygame.display.set_mode()

snowflakes = []
for i in range(10):
    snowflakes.append(load_img(f"assets/textures/snowflakes/snowflake_{i}.png", 2))

pygame.display.quit()
