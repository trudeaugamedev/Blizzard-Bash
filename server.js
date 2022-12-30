const WebSocket = require("ws");
function randint(min, max) {
	return Math.floor(Math.random() * (max - min + 1)) + min;
}

function broadcast(msg) {
	for (const client of players.values()) {
		client.socket.send(msg);
	}
}

// Exclusive broadcast
function xbroadcast(xid, msg) {
	for (const [id, client] of players) {
		if (id == xid) continue;
		client.socket.send(msg);
	}
}

class Player {
	constructor (client) {
		this.id = client.id;
		this.socket = client.socket;
		this.data = "";
	}
}

const wss = new WebSocket.Server({
	port: parseInt(process.env.PORT, 10) || 3000
});
const players = new Map();

let nextId = 0;

wss.on("connection", (socket) => {
    const client = {
		id: nextId++,
		socket: socket
	};

	players.set(client.id, new Player(client));
	console.log(`Client ${client.id} connected`);
    socket.send(`hi ${client.id}`);

	socket.on("error", (error) => {
		console.error(error);
	});

	socket.on("close", (code) => {
		players.delete(client.id);
		socket.close();
		console.log(`Client ${client.id} disconnected, code ${code}`);
	});

	socket.on("message", (msg) => {
		console.log(`Client ${client.id}: ${msg.toString()}`);
	});
});

// setInterval(main, 16);
setInterval(main, 3000);

function main() {
	broadcast("Hello from the server!");
}
