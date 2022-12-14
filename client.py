from websocket import WebSocketApp
from threading import Thread

from manager import GameManager

class Client:
    def __init__(self) -> None:
        self.socket = WebSocketApp("ws://192.168.0.88:1200/", on_message=self.on_message)
        self.socket_thread = Thread(target=self.socket.run_forever, daemon=True)

    def run(self) -> None:
        self.socket_thread.start()
        self.run_game()

    def on_message(self, ws, message: str) -> None:
        parsed = message.split()
        match parsed[0]:
            case "hi": # Connection signal
                print("Connected to server!")
            case "dc": # Disconnection signal
                print(f"Client {parsed[1]} disconnected!")
                self.manager.other_players[int(parsed[1])].kill()
                del self.manager.other_players[int(parsed[1])]
            case "cl": # Client data signal
                # try:
                    self.manager.parse(message)
                # except: # Invalid message
                #     print(f"Invalid message: '{message}'")

    def run_game(self) -> None:
        self.manager = GameManager(self)
        self.manager.run()

    def quit(self) -> None:
        self.socket.close()