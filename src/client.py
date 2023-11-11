from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .manager import GameManager

from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
import websockets.client as ws_client
from traceback import print_exc
from random import randint
from queue import Queue
import asyncio
import json

class ManualExit(Exception):
    def __str__(self) -> str:
        return super().__str__()

class Client:
    def __init__(self, manager: GameManager) -> None:
        self.manager = manager
        self.thread_data = Queue()
        self.running = True # Modify this attribute to stop client
        self.exited = False # Indicates whether the client has really exited

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
        print(data)
        self.thread_data.put_nowait(data)

    async def send(self) -> None:
        await asyncio.sleep(3)
        await self.socket.send(json.dumps({"client": "player", "name": f"DaNub_{randint(0, 2 ** 32)}"}))

    async def connect(self) -> None:
        print("Coroutine 'connect' started")
        self.socket = await ws_client.connect("ws://localhost:3000")
        print("Coroutine 'connect' exited")

    async def main(self) -> None:
        try:
            await asyncio.create_task(self.connect())
            await asyncio.gather(self.send_wrapper(), self.recv_wrapper())
        except ConnectionClosedError:
            print("Connection to the server was forcibly closed!")
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