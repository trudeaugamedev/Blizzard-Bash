import pygame

from exe import pathof

def load_img(file: str, factor: float = 4):
    return pygame.transform.scale_by(pygame.image.load(pathof(file)).convert_alpha(), factor)

pygame.display.set_mode()

snowflakes = []
for i in range(10):
    snowflakes.append(load_img(f"assets/textures/snowflakes/snowflake_{i}.png", 2))

pygame.display.quit()