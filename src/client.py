from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .manager import GameManager

from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
import websockets.client as ws_client
from traceback import print_exc
from threading import Thread
from queue import Queue
from typing import Any
import asyncio
import json
import time

from src.data_parser import Parser

class ManualExit(Exception):
    def __str__(self) -> str:
        return super().__str__()

class Client:
    def __init__(self, manager: GameManager) -> None:
        self.manager = manager
        self.reset()

    def reset(self) -> None:
        self.thread = Thread(target=self.run, daemon=True)
        self.parser = Parser(self)
        self.running = True # Modify this attribute to stop client
        self.exited = False # Indicates whether the client has really exited
        self.id = -2
        self.pers_data = { # Persistent data
            "name": None,
            "colors": None,
            "pos": None,
            "rot": None,
            "flip": None,
            "frame": None,
            "snowballs": None,
            "score": None,
        }
        self.modified_data = {key: True for key in self.pers_data}
        self.irreg_data = Queue() # Occasional data
        self.send_all_time = time.time()

    def restart(self) -> None:
        self.reset()
        self.thread.start()

    def queue_data(self, key: str, value: Any) -> None:
        if value == self.pers_data[key]: return
        self.pers_data[key] = value
        self.modified_data[key] = True

    async def recv_wrapper(self) -> None:
        print("Coroutine 'recv' started")
        try:
            while self.socket.open:
                await self.recv()
                if not self.running:
                    raise ManualExit
        except asyncio.CancelledError as error:
            print("Exiting 'recv' coroutine")
            raise error

    async def send_wrapper(self) -> None:
        print("Coroutine 'send' started")
        try:
            while self.socket.open:
                await self.send()
                if not self.running:
                    raise ManualExit
        except asyncio.CancelledError as error:
            print("Exiting 'send' coroutine")
            raise error

    async def recv(self) -> None:
        data = json.loads(await self.socket.recv())
        try:
            self.parser.parse(data)
        except AttributeError:
            pass

    async def send(self) -> None:
        await asyncio.sleep(0.014) # Slightly higher than 60 FPS

        final = {}
        for key in self.modified_data:
            if self.pers_data[key] is None: continue
            if self.modified_data[key]:
                final[key] = self.pers_data[key]
                self.modified_data[key] = False

        if time.time() - self.send_all_time > 3:
            final.update(self.pers_data)
            self.send_all_time = time.time()

        if final:
            await self.socket.send(json.dumps({"id": self.id} | final))

        while self.irreg_data.qsize() > 0:
            item = {"type": "ir"} | self.irreg_data.get()
            await self.socket.send(json.dumps(item))

    async def connect(self) -> None:
        print("Coroutine 'connect' started")
        # self.socket = await ws_client.connect("ws://localhost:3000")
        self.socket = await ws_client.connect("wss://trudeaugamedev-winter.herokuapp.com")
        print("Coroutine 'connect' completed")

    async def main(self) -> None:
        try:
            await asyncio.create_task(self.connect())
            await asyncio.gather(self.send_wrapper(), self.recv_wrapper())
        except ConnectionClosedError:
            print("Connection to the server was forcibly closed!")
            try:
                self.manager.new_scene("StartMenu")
            except Exception:
                print("Redirecting to start menu...")
        except ConnectionClosedOK:
            print("Cleanly disconnected from the server")
        except ManualExit:
            print("MANUAL EXIT")
        except:
            print_exc()
        finally:
            await self.quit()

    def run(self) -> None:
        asyncio.run(self.main())

    async def quit(self) -> None:
        print("QUITTING")
        if self.socket.open:
            await self.socket.close()
        self.exited = True