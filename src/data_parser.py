from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .manager import GameManager

from src.constants import VEC

class Parser:
    def __init__(self, manager: GameManager) -> None:
        self.manager = manager

    def parse(self, data: dict) -> None:
        match data["type"]:
            case "hi":
                self.manager.id = data["id"]
            case "cl":
                players = data["players"]
                if players and players[0]:
                    pos = players[0]["pos"]
                    self.manager.scene.pos = VEC(pos)