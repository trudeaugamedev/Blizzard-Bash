from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from client import Client

from pygame.locals import HWSURFACE, DOUBLEBUF, RESIZABLE, SCALED, WINDOWRESIZED, WINDOWMOVED, QUIT
from websocket._exceptions import WebSocketConnectionClosedException
from enum import Enum
import pygame
import sys

from .others import OtherPlayer, OtherSnowball, OtherPowerup
from .constants import WIDTH, HEIGHT, FPS, VEC
from .main_game import MainGame
from .end_menu import EndMenu
from .scene import Scene
from . import assets

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
        # Received format:
        # cl [id] [score] [x],[y];[rotation];[flip];[frame] [sb_x],[sb_y];[sb_frame];[sb_type]|<repeat> [powerup_x],[powerup_y]
        parsed = msg.split()
        i = int(parsed[1])

        p_data = parsed[3].split(";")
        p_pos = VEC(tuple(map(int, p_data[0].split(","))))
        p_rot = int(p_data[1])
        p_flip = bool(int(p_data[2]))
        p_frame = int(p_data[3])
        if i in self.other_players:
            self.other_players[i].pos = p_pos
            self.other_players[i].rotation = p_rot
            self.other_players[i].flip = p_flip
            self.other_players[i].frame = p_frame
        else:
            self.other_players[i] = OtherPlayer(self.scene, p_pos)
        player = self.other_players[i]

        player.score = int(parsed[2])

        if parsed[4] != "_":
            sb_data = parsed[4].split("|")
            for snowball in player.snowballs:
                snowball.kill()
            player.snowballs = []
            for i, data in enumerate(sb_data):
                data = data.split(";")
                sb_pos = VEC(tuple(map(int, data[0].split(","))))
                sb_frame = int(data[1])
                sb_type = assets.snowball_large if int(data[2]) else assets.snowball_small
                player.snowballs.append(OtherSnowball(self.scene, sb_pos))
                player.snowballs[i].pos = sb_pos
                player.snowballs[i].frame = sb_frame
                player.snowballs[i].type = sb_type
        elif player.snowballs:
            for snowball in player.snowballs:
                snowball.kill()
            player.snowballs = []

        if parsed[5] != "_":
            pw_pos = tuple(map(int, parsed[5].split(",")))
            if not player.powerup:
                player.powerup = OtherPowerup(self.scene, pw_pos)
            player.powerup.pos = VEC(pw_pos)
        elif player.powerup:
            player.powerup.kill()
            player.powerup = None

    def send(self) -> None:
        scene = self.scene.previous_scene if isinstance(self.scene, self.Scenes.EndMenu.value) else self.scene

        score = scene.score

        p_pos = f"{int(scene.player.pos.x)},{int(scene.player.pos.y)}"
        p_rot = f"{int(scene.player.rotation)}"
        p_flip = f"{int(scene.player.flip)}"
        p_frame = f"{(assets.player.index(scene.player.orig_image))}"
        p_data = f"{p_pos};{p_rot};{p_flip};{p_frame}"

        if scene.player.snowballs:
            sb_data = ""
            for snowball in scene.player.snowballs:
                sb_pos = f"{int(snowball.pos.x)},{int(snowball.pos.y)}"
                sb_frame = snowball.frame
                sb_type = 0 if snowball.type == assets.snowball_small else 1
                sb_data += f"{sb_pos};{sb_frame};{sb_type}|"
            sb_data = sb_data[:-1]
        else:
            sb_data = "_"

        if scene.powerup:
            pw_pos = f"{int(scene.powerup.pos.x)},{int(scene.powerup.pos.y)}"
        else:
            pw_pos = "_"

        try:
            self.client.socket.send(f"{score} {p_data} {sb_data} {pw_pos}")
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
        EndMenu = EndMenu
