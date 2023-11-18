from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client

from src.others import OtherPlayer, OtherSnowball
from src.powerup import Powerup
from src.constants import VEC

class Parser:
    def __init__(self, client: Client) -> None:
        self.client = client
        self.manager = client.manager

    def parse(self, data: dict) -> None:
        match data["type"]:
            case "hi": # Initial
                self.client.id = data["id"]
                self.manager.scene.seed = data["seed"]
                self.manager.scene.waiting = data["waiting"]
            case "cl": # Client data
                self.client_data(data)
            case "ir": # Irregular client data
                self.irregular_client_data(data)
            case "ad": # Admin command
                if data["command"] == "start":
                    self.manager.scene.waiting = False
                elif data["command"] == "stop":
                    self.manager.scene.time_left = -1
            case "wd": # Wind
                self.manager.scene.wind_vel = VEC(data["speed"], 0)
            case "tm": # Time
                self.manager.scene.time_left = data["seconds"]
            case "el": # Eliminated
                self.manager.scene.player.eliminated = True

    def client_data(self, data: dict) -> None:
        if not isinstance(self.manager.scene, self.manager.Scenes.MainGame.value): return

        all_ids = set(self.manager.other_players.keys())
        for player_data in data["players"]:
            if not player_data: continue

            if player_data["id"] in all_ids:
                all_ids.remove(player_data["id"])

            # Parse data of player itself
            if player_data["id"] in self.manager.other_players:
                other: OtherPlayer = self.manager.other_players[player_data["id"]]
                other.pos = player_data["pos"]
                other.rotation = player_data["rot"]
                other.flip = player_data["flip"]
                other.frame = player_data["frame"]
                other.score = player_data["score"]
            else:
                other = self.manager.other_players[player_data["id"]] = OtherPlayer(self.manager.scene, player_data["id"], player_data["pos"])

            # Parse data of snowballs
            for snowball in other.snowballs:
                snowball.kill()
            other.snowballs = []
            for data in player_data["snowballs"]:
                other.snowballs.append(
                    OtherSnowball(self.manager.scene, data["pos"], data["frame"], data["type"])
                )

        # Remove disconnected players
        for _id in all_ids:
            self.manager.other_players.pop(_id).kill()

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