from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client

from src.others import OtherPlayer, OtherSnowball
from src.constants import VEC

class Parser:
    def __init__(self, client: Client) -> None:
        self.client = client
        self.manager = client.manager

    def parse(self, data: dict) -> None:
        match data["type"]:
            case "hi":
                self.client.id = data["id"]
            case "cl":
                self.client_data(data)

    def client_data(self, data: dict) -> None:
        for player_data in data["players"]:
            if not player_data: continue

            # Parse data of player itself
            if player_data["id"] in self.manager.other_players:
                other: OtherPlayer = self.manager.other_players[player_data["id"]]
                other.pos = player_data["pos"]
                other.rotation = player_data["rot"]
                other.flip = player_data["flip"]
                other.frame = player_data["frame"]
            else:
                other = self.manager.other_players[player_data["id"]] = OtherPlayer(self.manager.scene, player_data["pos"])

            # Parse data of snowballs
            for snowball in other.snowballs:
                snowball.kill()
            other.snowballs = []
            for data in player_data["snowballs"]:
                other.snowballs.append(
                    OtherSnowball(self.manager.scene, data["pos"], data["frame"], data["type"])
                )