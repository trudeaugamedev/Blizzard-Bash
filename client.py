from websocket import WebSocketApp
from threading import Thread

from manager import GameManager

class Client:
    def __init__(self) -> None:
        self.socket = WebSocketApp("ws://192.168.0.46:1211/", on_message=self.on_message)
        self.socket_thread = Thread(target=self.socket.run_forever)

    def run(self) -> None:
        self.socket_thread.start()
        self.run_game()

    def on_message(self, ws, message) -> None:
        try:
            self.manager.recv(message)
        except: # Invalid message
            print("Invalid")

    def run_game(self) -> None:
        self.manager = GameManager(self)
        self.manager.run()