from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .client import Client

from src.others import OtherPlayer, OtherSnowball, OtherVortex
from src.powerup import Powerup
from src.constants import VEC

from websockets.exceptions import ConnectionClosedError
import time

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
                    self.manager.scene.player.powerup_time = 0
                    while self.manager.scene.player.snowball_queue:
                        self.manager.scene.player.pop_snowball()
                    self.manager.scene.player.dig_iterations = 0
                elif data["command"] == "stop":
                    self.manager.scene.time_left = -1
            case "tp": # teleport
                self.manager.scene.player.pos = data["tppos"]
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

            if init:
                player = OtherPlayer(self.manager.scene, player_data["id"], player_data["pos"])
                self.manager.other_players[player_data["id"]] = player
            if player_data["id"] not in self.manager.other_players:
                try:
                    player = OtherPlayer(self.manager.scene, player_data["id"], player_data["pos"])
                    self.manager.other_players[player_data["id"]] = player
                except KeyError:
                    continue
            other = self.manager.other_players[player_data["id"]]
            other.disconnect_time = time.time()

            if "name" in player_data and player_data["name"] is not None: other.name = player_data["name"]
            if "pos" in player_data and player_data["pos"] is not None: other.pos = VEC(player_data["pos"])
            if "rot" in player_data and player_data["rot"] is not None: other.rotation = player_data["rot"]
            if "flip" in player_data and player_data["flip"] is not None: other.flip = player_data["flip"]
            if "frame" in player_data and player_data["frame"] is not None: other.frame = player_data["frame"]
            if "score" in player_data and player_data["score"] is not None: other.score = player_data["score"]
            if "powerup" in player_data and player_data["powerup"] is not None: other.powerup = player_data["powerup"]
            if "colors" in player_data and player_data["colors"] is not None: other.set_colors(*player_data["colors"])

            if "snowballs" in player_data and player_data["snowballs"]:
                # Parse data of snowballs
                for snowball_data in player_data["snowballs"]:
                    if snowball_data["id"] in OtherSnowball.killed: continue
                    if snowball_data["id"] in other.snowballs:
                        snowball = other.snowballs[snowball_data["id"]]
                        snowball.pos = VEC(snowball_data["pos"])
                        snowball.frame = snowball_data["frame"]
                    else:
                        other.snowballs[snowball_data["id"]] = OtherSnowball(self.manager.scene, snowball_data["id"], snowball_data["pos"], snowball_data["frame"], snowball_data["type"])

            # # contains data for the image of the storm
            # if "storm_blobs" in player_data and player_data["storm_blobs"]:
            #     for data in player_data["storm_blobs"]:
            #         id = data["id"]
            #         if id in OtherVortex.instances:
            #             storm = OtherVortex.instances[id]
            #         else:
            #             OtherVortex.instances[id] = OtherVortex(self.manager.scene, id, None, None) # pos, alpha
            #             OtherVortex.instances[id].create_image(data["size"], data["offsets"], data["radii"])

            # continuous data for the storm
            # if "storms" in player_data and player_data["storms"]:
            #     for storm_data in player_data["storms"]:
            #         if storm_data["id"] in OtherVortex.instances:
            #             storm = OtherVortex.instances[storm_data["id"]]
            #             storm.pos = VEC(storm_data["pos"])
            #             storm.alpha = storm_data["alpha"]
            #         else:
            #             OtherVortex.instances[storm_data["id"]] = OtherVortex(self.manager.scene, storm_data["id"], storm_data["pos"], storm_data["alpha"])

        all_ids = set(Powerup.instances.keys())
        # Parse powerup position
        if "powerups" not in data: return
        if not data["powerups"]:
            for _id in all_ids:
                Powerup.instances.pop(_id).kill()
            return
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
        if "landed" in data:
            self.manager.other_players[data["player_id"]].snowballs.pop(data["snowball_id"]).kill()

        elif "hit" in data:
            self.manager.scene.player.hit_size = data["hit_size"]
            self.manager.scene.player.hit_strength = data["hit"]
            self.manager.scene.player.hit_powerup = data["hit_powerup"]
            self.manager.scene.frost_vignette.opacity += 70 * abs(data["hit"])

        elif "storm_id" in data:
            OtherVortex.instances.pop(data["storm_id"]).kill()