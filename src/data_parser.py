from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client

from src.others import OtherPlayer, OtherSnowball
from src.powerup import Powerup
from src.constants import VEC

from websockets.exceptions import ConnectionClosedError

class Parser:
    def __init__(self, client: Client) -> None:
        self.client = client
        self.manager = client.manager

    def parse(self, data: dict) -> None:
        # THIS SECTION MIGHT NOT RAISE EXCEPTIONS PROPERLY!!!!!!!!
        match data["type"]:
            case "hi": # Initial
                self.client.id = data["id"]
                self.manager.scene.seed = data["seed"]
                self.manager.scene.waiting = data["waiting"]
                if not data["waiting"]:
                    self.manager.scene.eliminated = True
                self.client_data(data["data"], init=True)
            case "cl": # Client data
                self.client_data(data)
            case "ir": # Irregular client data
                self.irregular_client_data(data)
            case "ad": # Admin command
                if data["command"].startswith("start"):
                    self.manager.scene.waiting = False
                    self.manager.scene.player.powerup = None
                elif data["command"] == "stop":
                    self.manager.scene.time_left = -1
            case "wd": # Wind
                self.manager.scene.wind_vel = VEC(data["speed"], 0)
            case "tm": # Time
                self.manager.scene.time_left = data["seconds"]
            case "el": # Eliminated
                self.manager.scene.eliminated = True
            case "cn": # Connect
                self.manager.other_players[data["id"]] = OtherPlayer(self.manager.scene, data["id"], (0, -3000))
            case "dc": # Disconnect
                if data["id"] in self.manager.other_players:
                    self.manager.other_players.pop(data["id"]).kill()
            case "en": # End (game over)
                print("GAME OVER")
                self.manager.scene.score_data = data["data"]
                self.manager.scene.game_over = True
            case "kc": # Kick
                print("KICKED")
                raise ConnectionClosedError(None, None)

    def client_data(self, data: dict, init: bool = False) -> None:
        if not init and not isinstance(self.manager.scene, self.manager.Scenes.MainGame.value): return

        for player_data in data["players"]:
            if not player_data: continue

            if init: self.manager.other_players[player_data["id"]] = OtherPlayer(self.manager.scene, player_data["id"], player_data["pos"])
            if player_data["id"] not in self.manager.other_players: continue
            other = self.manager.other_players[player_data["id"]]

            if "name" in player_data: other.name = player_data["name"]
            if "pos" in player_data: other.pos = VEC(player_data["pos"])
            if "rot" in player_data: other.rotation = player_data["rot"]
            if "flip" in player_data: other.flip = player_data["flip"]
            if "frame" in player_data: other.frame = player_data["frame"]
            if "score" in player_data: other.score = player_data["score"]

            if "snowballs" in player_data:
                # Parse data of snowballs
                for snowball in other.snowballs:
                    snowball.kill()
                other.snowballs = []
                for snowball_data in player_data["snowballs"]:
                    other.snowballs.append(
                        OtherSnowball(self.manager.scene, snowball_data["pos"], snowball_data["frame"], snowball_data["type"])
                    )

        all_ids = set(Powerup.instances.keys())
        # Parse powerup position
        if "powerups" not in data: return
        for powerup_data in data["powerups"]:
            if powerup_data["id"] in all_ids:
                all_ids.remove(powerup_data["id"])

            if powerup_data["id"] in Powerup.instances:
                powerup = Powerup.instances[powerup_data["id"]]
                powerup.recv_pos = VEC(powerup_data["pos"])
            else:
                Powerup.instances[powerup_data["id"]] = Powerup(self.manager.scene, powerup_data["id"], powerup_data["type"], powerup_data["pos"])

        for _id in all_ids:
            Powerup.instances.pop(_id).kill()

    def irregular_client_data(self, data: dict) -> None:
        if "hit" in data:
            self.manager.scene.player.hit_strength = data["hit"]
            self.manager.scene.frost_vignette.opacity += 70 * abs(data["hit"])