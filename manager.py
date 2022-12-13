from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from client import Client

from pygame.locals import HWSURFACE, DOUBLEBUF, RESIZABLE, SCALED, WINDOWRESIZED, WINDOWMOVED, QUIT
from enum import Enum
import pygame
import sys

from constants import WIDTH, HEIGHT, FPS
from main_game import MainGame
from scene import Scene

class AbortScene(Exception):
    def __str__(self):
        return "Scene aborted but not caught with a try/except block."

class GameManager:
    def __init__(self, client: Client) -> None:
        pygame.init()

        self.client = client
        self.flags = HWSURFACE | DOUBLEBUF | RESIZABLE | SCALED
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), self.flags)
        self.clock = pygame.time.Clock()
        self.dt = self.clock.tick_busy_loop(FPS) / 1000
        self.window_changing = False
        self.events = []
        self.scene = MainGame(self, None)
        self.other_players = {}

    def run(self) -> None:
        while self.scene.running:
            self.update()
            try:
                self.scene.update()
                self.scene.draw()
            except AbortScene:
                pass

    def update(self) -> None:
        self.dt = self.clock.tick_busy_loop(FPS) / 1000
        # Window changing events only register to the DT the frame after the event
        # Thus the window changing variable is "sustained" to the next frame, and handled here
        if self.window_changing:
            self.dt = 0
            self.window_changing = False

        pygame.display.set_caption(f"Winter Game | FPS: {round(self.clock.get_fps())}")

        self.events = {event.type: event for event in pygame.event.get()}

        if QUIT in self.events:
            self.quit()
        if WINDOWRESIZED in self.events or WINDOWMOVED in self.events:
            self.window_changing = True
            self.dt = 0

        pygame.display.flip()

    def recv(self, msg: str) -> None:
        print(msg)

    def send(self) -> None:
        self.client.socket.send(f"{self.scene.player.pos}")

    def quit(self) -> None:
        pygame.quit()
        sys.exit()

    def new_scene(self, scene_class: str) -> None:
        self.scene.running = False
        self.scene = self.Scenes[scene_class].value(self, self.scene)
        raise AbortScene

    def switch_scene(self, scene: Scene) -> None:
        self.scene.running = False
        self.scene = scene
        self.scene.running = True
        raise AbortScene

    class Scenes(Enum):
        MainGame = MainGame