const { WebSocketServer } = require("ws");

let nextid = 0;

const wss = new WebSocketServer({
	port: parseInt(process.env.PORT, 10) || 3000,
});

const clients = new Map();

function broadcast(msg) {
	for (const client of clients.values()) {
		client.socket.send(msg);
	}
}

// Exclusive broadcast
function xbroadcast(xid, msg) {
	for (const [id, client] of clients) {
		if (id == xid) {
			continue;
		}
		client.socket.send(msg);
	}
}

wss.on("connection", (socket) => {
	const client = {
		id: nextid++,
		socket: socket
	};
	clients.set(client.id, client);
	console.log(`Client ${client.id} connected`);
	socket.on("error", (error) => {
		console.error(error);
	});
	socket.on("close", (code) => {
		clients.delete(client.id);
		socket.close();
		console.log(`Client ${client.id} disconnected, code ${code}`);
		broadcast(`dc ${client.id}`);
	});
	socket.on("message", (msg) => {
		xbroadcast(client.id, `cl ${client.id} ${msg}`);
	});

	socket.send("hi");
});
