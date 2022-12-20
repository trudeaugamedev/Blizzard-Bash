from websocket import WebSocketApp
from threading import Thread

from .manager import GameManager

class Client:
    def __init__(self) -> None:
        # self.socket = WebSocketApp("ws://localhost:3000", on_message=self.on_message, on_error=self.on_error)
        self.socket = WebSocketApp("wss://trudeaugamedev-winter.herokuapp.com", on_message=self.on_message)
        self.socket_thread = Thread(target=self.socket.run_forever, daemon=True)
        self.thread_data = {}

    def run(self) -> None:
        self.socket_thread.start()
        self.run_game()

    def on_message(self, ws, message: str) -> None:
        parsed = message.split()
        match parsed[0]:
            case "hi": # Connection signal
                print("Connected to server!")
                self.thread_data["id"] = int(parsed[1])
                self.thread_data["seed"] = int(parsed[2])
            case "dc": # Disconnection signal
                print(f"Client {parsed[1]} disconnected!")
                self.manager.other_players[int(parsed[1])].kill()
                del self.manager.other_players[int(parsed[1])]
            case "wd": # New wind speed
                self.thread_data["wind"] = int(parsed[1])
            case "rd": # Everyone ready, game starts
                self.thread_data["ready"] = True
            case "el": # Eliminate a player
                self.thread_data["eliminate"] = True
            case "cl": # Client data signal
                self.manager.parse(message)

    def on_error(self, ws, error):
        print(error)

    def run_game(self) -> None:
        self.manager = GameManager(self)
        self.manager.run()

    def quit(self) -> None:
        self.socket.close()
