from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client

from src.others import OtherPlayer
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
        for player in data["players"]:
            if not player: continue
            if player["id"] in self.manager.other_players:
                other = self.manager.other_players[player["id"]]
                other.pos = player["pos"]
                other.rotation = player["rot"]
                other.flip = player["flip"]
            else:
                self.manager.other_players[player["id"]] = OtherPlayer(self.manager.scene, player["pos"])