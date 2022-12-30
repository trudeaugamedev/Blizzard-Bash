import websockets
import asyncio

from src.client import Client

if __name__ == "__main__":
    client = Client()
    try:
        asyncio.run(client.run())
    except KeyboardInterrupt:
        print("KEYBOARD INTERRUPT")
        print("\t--===<<<\t ABORTING PROGRAM \t>>>===--")
        asyncio.run(client.quit())
    except websockets.exceptions.ConnectionClosedError:
        print("Connection to the server was forcibly closed")
        print("\t--===<<<\t ABORTING PROGRAM \t>>>===--")
        asyncio.run(client.quit())