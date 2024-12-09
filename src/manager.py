from pygame.locals import *
from enum import Enum
import asyncio
import pygame
import sys

from .constants import WIDTH, HEIGHT, FPS
from .start_menu import StartMenu
from .main_game import MainGame
from .profiling import profile
from .end_menu import EndMenu
from .client import Client
from .sprite import Layers
from .scene import Scene
from . import assets

class AbortScene(Exception):
    def __str__(self):
        return "Scene aborted but not caught with a try/except block."

class GameManager:
    def __init__(self) -> None:
        pygame.init()
        pygame.key.set_repeat(500, 25)
        pygame.mouse.set_cursor((19, 19), assets.crosshair)

        self.client = Client(self)

        self.flags = HWSURFACE | DOUBLEBUF | RESIZABLE | SCALED | FULLSCREEN
        self.window = pygame.display.set_mode((WIDTH, HEIGHT), self.flags)
        self.screen = pygame.Surface((4800, HEIGHT + 250), SRCALPHA)
        self.clock = pygame.time.Clock()
        self.dt = self.clock.tick_busy_loop(FPS) / 1000
        self.window_changing = False
        self.events = []
        self.other_players = {}
        self.scene = StartMenu(self, None)
        self.ready = False

    def run(self) -> None:
        while self.scene.running:
            self.update()
            try:
                if K_F12 in self.key_downs:
                    profile(self.scene.update)
                else:
                    self.scene.update()
                if K_F11 in self.key_downs:
                    profile(self.scene.draw)
                else:
                    self.scene.draw()
            except AbortScene:
                pass
            h = WIDTH / self.screen.get_width() * self.screen.get_height()
            self.window.blit(pygame.transform.scale(self.screen, (WIDTH, h)), (0, HEIGHT - h + 25))

    def update(self) -> None:
        self.dt = self.clock.tick_busy_loop(FPS) / 1000
        # Window changing events only register to the DT the frame after the event
        # Thus the window changing variable is "sustained" to the next frame, and handled here
        if self.window_changing:
            self.dt = 0
            self.window_changing = False

        pygame.display.set_caption(f"Blizzard Bash | FPS: {round(self.clock.get_fps())}")

        self.events = {event.type: event for event in pygame.event.get()}
        self.key_downs = {event.key: event for event in self.events.values() if event.type == KEYDOWN}
        self.key_ups = {event.key: event for event in self.events.values() if event.type == KEYUP}
        self.key_presses = pygame.key.get_pressed()

        if QUIT in self.events:
            self.quit()
        if WINDOWRESIZED in self.events or WINDOWMOVED in self.events:
            self.window_changing = True
            self.dt = 0

        pygame.display.flip()

    def quit(self) -> None:
        self.client.running = False
        print("Quitting Pygame")
        pygame.quit()
        print("Waiting for client to exit")
        print("Client has exited")
        sys.exit()

    def new_scene(self, scene_class: str) -> None:
        self.scene.running = False
        self.scene = self.Scenes[scene_class].value(self, self.scene)
        self.scene.setup()
        raise AbortScene

    def switch_scene(self, scene: Scene) -> None:
        self.scene.running = False
        self.scene = scene
        self.scene.running = True
        raise AbortScene

    class Scenes(Enum):
        StartMenu = StartMenu
        MainGame = MainGame
        EndMenu = EndMenu
