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
		if (client.id === -1) console.log(`Admin has disconnected, code ${code}`);
		else console.log(`Client ${client.id} disconnected, code ${code}`);
	});

	socket.on("message", (msg) => {
		if (msg.toString() === "admin") {
			console.log("Admin has connected");
			// Move the admin player object to -1
			players.set(-1, players.get(client.id));
			players.delete(client.id);
			// Change IDs
			players.get(-1).id = -1;
			client.id = -1;
			nextId--;
			return;
		}
		if (client.id != -1) {
			const data = JSON.parse(msg.toString());
			players.get(client.id).data = data;
			console.log(`Client ${client.id}: ${JSON.stringify(players.get(client.id).data)}`);
		} else {
			const command = msg.toString();
			broadcast(command);
			console.log(`Admin sent the command "${command}"`);
		}
	});
});

function game() {
	broadcastPlayerData();
}

// setInterval(game, 16);
setInterval(game, 2000);