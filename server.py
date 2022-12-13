from websocket_server import WebsocketServer as Server

def send(client: dict, msg: str) -> None:
    server.send_message(client, msg)

def broadcast(msg: str) -> None:
    for client in clients:
        server.send_message(client, msg)

# Exclusive broadcast
def xbroadcast(client: dict, msg: str) -> None:
    for other in clients:
        if other == client: continue
        server.send_message(other, msg)

def new_client(client: dict, server: Server):
    print(f"Client {client['id']} at {client['address']} has joined!")
    server.send_message(client, "Hello from the server!")

def new_message(client: dict, server: Server, msg: str):
    xbroadcast(client, msg)

clients = []

server = Server("0.0.0.0", 1211)
server.set_fn_new_client(new_client)
server.set_fn_message_received(new_message)
server.run_forever()