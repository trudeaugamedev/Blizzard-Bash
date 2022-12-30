const WebSocket = require("ws");
function randint(min, max) {
	return Math.floor(Math.random() * (max - min + 1)) + min;
}

function broadcast(msg) {
	for (const player of players.values()) {
		player.socket.send(msg);
	}
}

function broadcastPlayerData() {
	for (const [id, player] of players) {
		let xplayers = new Map(players);
		xplayers.delete(id);
		let dataArray = Array.from(xplayers.values()).map(player => player.data);
		player.socket.send(JSON.stringify(dataArray));
	}
}

WebSocket.WebSocket.prototype.send_obj = function send_obj (obj) {
	this.send(JSON.stringify(obj));
}

class Player {
	constructor (client) {
		this.id = client.id;
		this.socket = client.socket;
		this.data = null;
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
    socket.send_obj({"id": client.id});

	socket.on("error", (error) => {
		console.error(error);
	});

	socket.on("close", (code) => {
		players.delete(client.id);
		socket.close();
		console.log(`Client ${client.id} disconnected, code ${code}`);
	});

	socket.on("message", (msg) => {
		const data = JSON.parse(msg.toString());
		players.get(client.id).data = data;
		console.log(`Client ${client.id}: ${JSON.stringify(players.get(client.id).data)}`);
	});
});

// setInterval(main, 16);
setInterval(main, 3000);

function main() {
	broadcastPlayerData();
}
