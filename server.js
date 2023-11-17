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
		player.socket.send(JSON.stringify({"type": "cl", "players": dataArray}));
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

let seed = randint(0, 99999999);
let nextId = 0;
let waiting = true;

let wind_time = Date.now();
let wind_duration = randint(4000, 8000);
let wind_speed = [randint(-600, -200), randint(200, 600)][randint(0, 1)];

let start_time, timer_time;

wss.on("connection", (socket) => {
    const client = {
		id: nextId++,
		socket: socket
	};

	players.set(client.id, new Player(client));
	console.log(`Client ${client.id} connected`);
    socket.send_obj({"type": "hi", "id": client.id, "seed": seed});

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
			handleAdminConnect(client);
			return;
		}

		if (client.id == -1) {
			handleAdminMessage(msg);
			return;
		}

		const data = JSON.parse(msg.toString());
		if (data.type === "ir") {
			if (data.hit) {
				players.get(data.id).socket.send(JSON.stringify(data));
			}
		}
		players.get(client.id).data = data;
		// console.log(`Client ${client.id}: ${JSON.stringify(players.get(client.id).data)}`);
	});
});

function handleAdminConnect(client) {
	console.log("Admin has connected");
	// Move the admin player object to -1, since it was added as a normal player on connection
	players.set(-1, players.get(client.id));
	players.delete(client.id);
	// Change IDs
	players.get(-1).id = -1;
	client.id = -1;
	nextId--;
}

function handleAdminMessage(msg) {
	const command = msg.toString();
	if (command === "start") {
		waiting = false;
		timer_time = Date.now();
		start_time = Date.now();
	}
	broadcast(JSON.stringify({"type": "ad", "command": command}));
	console.log(`Admin sent the command "${command}"`);
}

function game() {
	broadcastPlayerData();

	if (Date.now() - wind_time > wind_duration) {
		wind_time = Date.now();
		wind_duration = randint(3000, 6000);
		wind_speed = [randint(-600, -200), randint(200, 600)][randint(0, 1)];
		broadcast(JSON.stringify({"type": "wd", "speed": wind_speed}));
	}

	if (Date.now() - timer_time > 1000) {
		timer_time = Date.now();
		broadcast(JSON.stringify({"type": "tm", "seconds": Math.floor((300000 - (Date.now() - start_time)) / 1000)}));
	}
}

setInterval(game, 12);