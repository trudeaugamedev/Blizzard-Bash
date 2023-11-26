from .sprite import VisibleSprite, Layers
from .scene import Scene
from . import assets

class FrostVignette(VisibleSprite):
    def __init__(self, scene: Scene) -> None:
        super().__init__(scene, Layers.VIGNETTE)
        self.image = assets.frost_vignette
        self.opacity = 0

    def update(self) -> None:
        self.opacity *= 0.8 ** self.manager.dt
        if self.opacity > 320:
            self.opacity = 320
        elif self.opacity < 0:
            self.opacity = 0
        self.image.set_alpha(self.opacity)

    def draw(self) -> None:
        if self.opacity == 0: return
        self.manager.screen.blit(self.image, (0, 0))