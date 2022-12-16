from websocket_server import WebsocketServer as Server

def send(client: dict, msg: str) -> None:
    server.send_message(client, msg)

def broadcast(msg: str) -> None:
    for client in clients.values():
        server.send_message(client, msg)

# Exclusive broadcast
def xbroadcast(client: dict, msg: str) -> None:
    for other in clients.values():
        if other == client: continue
        server.send_message(other, msg)

def new_client(client: dict, server: Server):
    print(f"Client {client['id']} at {client['address']} connected!")
    clients[client["id"]] = client
    send(client, "hi")

def client_left(client: dict, server: Server):
    print(f"Client {client['id']} at {client['address']} disconnected!")
    del clients[client["id"]]
    broadcast(f"dc {client['id']}")

def new_message(client: dict, server: Server, msg: str):
    xbroadcast(client, f"cl {client['id']} {msg}")

clients = {}

server = Server("192.168.0.88", 1200)
server.set_fn_new_client(new_client)
server.set_fn_message_received(new_message)
server.set_fn_client_left(client_left)
server.run_forever()