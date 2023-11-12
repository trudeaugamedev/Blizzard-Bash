from pygame.locals import HWSURFACE, DOUBLEBUF, RESIZABLE, SCALED, WINDOWRESIZED, WINDOWMOVED, QUIT
from websocket._exceptions import WebSocketConnectionClosedException
from threading import Thread
from enum import Enum
import asyncio
import pygame
import time
import sys

from .others import OtherPlayer, OtherSnowball, OtherPowerup
from .constants import WIDTH, HEIGHT, FPS, VEC
from .client import Client, ManualExit
from .main_game import MainGame
from .end_menu import EndMenu
from .scene import Scene
from . import assets

class AbortScene(Exception):
    def __str__(self):
        return "Scene aborted but not caught with a try/except block."

class GameManager:
    def __init__(self) -> None:
        pygame.init()

        self.client = Client(self)

        self.flags = HWSURFACE | DOUBLEBUF | RESIZABLE | SCALED
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), self.flags)
        self.clock = pygame.time.Clock()
        self.dt = self.clock.tick_busy_loop(FPS) / 1000
        self.window_changing = False
        self.events = []
        self.other_players = {}
        self.scene = MainGame(self, None)
        self.ready = False
        self.id = -1

        self.client_thread = Thread(target=self.client.run, daemon=True)
        self.client_thread.start()

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

        pygame.display.set_caption(f"Blizzard Bash | FPS: {round(self.clock.get_fps())}")

        self.events = {event.type: event for event in pygame.event.get()}

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
        while not self.client.exited:
            time.sleep(0.1)
        print("Client has exited")
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
        EndMenu = EndMenu
