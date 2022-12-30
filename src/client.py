import websockets.client as ws_client
from threading import Thread
import websockets
import asyncio
import time
import sys

from .manager import GameManager

class Client:
    def __init__(self) -> None:
        self.thread = Thread(target=self.async_thread, daemon=True)
        self.thread_data = {}

    def async_thread(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.receive())
        except websockets.exceptions.ConnectionClosedOK:
            # Not sure why this can't be catched along with
            # websockets.exceptions.ConnectionClosedError
            # in main.py but I guess we're catching it here
            pass
        loop.close()

    async def receive(self) -> None:
        self.socket = await ws_client.connect("ws://localhost:3000")
        while self.socket.open:
            data = await self.socket.recv()
            print(data)

    async def run(self) -> None:
        self.thread.start()
        # Temporary replacement for Manager.run
        while True:
            time.sleep(3)
            # Any error that happen here will actually occur now, where previously it was silently getting catched by the framework
            await self.socket.send("Hi :D")

    async def quit(self) -> None:
        print("\t--===<<<\t QUITTING \t>>>===--")
        try:
            await self.socket.close()
        except ValueError: # If it could not perform a closing handshake, meaning that the connection was foribly ended
            pass
        sys.exit()