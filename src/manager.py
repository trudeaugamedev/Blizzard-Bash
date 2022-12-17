from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from client import Client

from pygame.locals import HWSURFACE, DOUBLEBUF, RESIZABLE, SCALED, WINDOWRESIZED, WINDOWMOVED, QUIT
from websocket._exceptions import WebSocketConnectionClosedException
from enum import Enum
import pygame
import sys

from .others import OtherPlayer, OtherSnowball
from .constants import WIDTH, HEIGHT, FPS, VEC
from .main_game import MainGame
from .scene import Scene

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
        self.other_players = {}
        self.scene = MainGame(self, None)

    def run(self) -> None:
        while self.scene.running:
            self.update()
            try:
                self.scene.update()
                self.scene.draw()
            except AbortScene:
                pass
            self.send()

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

    def parse(self, msg: str) -> None:
        # Received format: "cl [id] [score] [x],[y] [snowball_x],[snowball_y];[snowball_frame]"
        parsed = msg.split()
        i = int(parsed[1])

        pos = tuple(map(int, parsed[3].split(",")))
        if i in self.other_players:
            self.other_players[i].pos = VEC(pos)
        else:
            self.other_players[i] = OtherPlayer(self.scene, pos)
        player = self.other_players[i]

        player.score = int(parsed[2])

        if parsed[4] != "_":
            sb_data = parsed[4].split(";")
            sb_pos = tuple(map(int, sb_data[0].split(",")))
            sb_frame = int(sb_data[1])
            if not player.snowball:
                player.snowball = OtherSnowball(self.scene, sb_pos)
            player.snowball.pos = VEC(sb_pos)
            player.snowball.frame = sb_frame
        else:
            player.snowball.kill()
            player.snowball = None

    def send(self) -> None:
        score = self.scene.score

        pos = f"{int(self.scene.player.pos.x)},{int(self.scene.player.pos.y)}"

        if self.scene.player.snowball:
            sb_pos = f"{int(self.scene.player.snowball.pos.x)},{int(self.scene.player.snowball.pos.y)}"
            sb_frame = self.scene.player.snowball.frame
            sb_data = f"{sb_pos};{sb_frame}"
        else:
            sb_data = "_"

        try:
            self.client.socket.send(f"{score} {pos} {sb_data}")
        except WebSocketConnectionClosedException:
            pass

    def quit(self) -> None:
        self.client.quit()
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
