from .sprite import VisibleSprite, Layers
from .scene import Scene
from . import assets

import pytweening as tween

class FrostVignette(VisibleSprite):
    def __init__(self, scene: Scene) -> None:
        super().__init__(scene, Layers.VIGNETTE)
        self.image = assets.frost_vignette
        self.opacity = 0

    def update(self) -> None:
        return
        self.opacity *= 0.8 ** self.manager.dt
        if self.opacity > 320:
            self.opacity = 320
        elif self.opacity < 0:
            self.opacity = 0
        self.image.set_alpha(self.opacity)

    def draw(self) -> None:
        return
        if self.opacity == 0: return
        self.manager.screen.blit(self.image, (0, 0))

class ElimVignette(VisibleSprite):
    def __init__(self, scene: Scene) -> None:
        super().__init__(scene, Layers.VIGNETTE)
        self.image = assets.elim_vignette
        self.progress = 0
        self.direction = 1
        self.opacity = 0
        self.flashing = False

    def update(self) -> None:
        return
        self.flashing = self.scene.time_left is not None and self.scene.time_left < self.scene.total_time / 2 and self.manager.other_players and min(map(lambda p: p.score, self.manager.other_players.values())) >= self.scene.score
        if not self.flashing:
            self.progress = 0
            self.direction = 1
            self.opacity = 0
            return

        self.progress += self.direction * 3 * self.manager.dt
        if self.progress > 1:
            self.progress = 1
            self.direction = -1
        elif self.progress < -0.5:
            self.progress = -0.5
            self.direction = 1
        self.opacity = tween.easeOutSine(max(self.progress, 0)) * 75

        self.image.set_alpha(self.opacity)

    def draw(self) -> None:
        return
        if self.opacity < 0 or self.scene.eliminated or not self.flashing or self.scene.waiting: return
        self.manager.screen.blit(self.image, (0, 0))