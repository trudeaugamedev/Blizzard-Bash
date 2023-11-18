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

		let playerDataArray = new Array(0);
		for (const [id, player] of xplayers) {
			if (player.eliminated) continue;
			playerDataArray.push(player.data);
		}

		let powerupDataArray = Array.from(powerups.values()).map(powerup => ({
			"id": powerup.id,
			"type": powerup.type,
			"pos": [Math.floor(powerup.pos[0]), Math.floor(powerup.pos[1])],
		}));

		player.socket.send(JSON.stringify({
			"type": "cl",
			"players": playerDataArray,
			"powerups": powerupDataArray,
		}));
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
		this.eliminated = false;
	}
}

class Powerup {
	constructor (id) {
		this.id = id;
		powerupId++;
		this.vel = [0, 0]
		this.pos = [randint(-1800, 1800), -800];
		this.type = ["rapidfire", "strength"][randint(0, 1)]
		this.startTime = Date.now();
	}

	update() {
		this.vel[1] += 0.01;
		this.pos[1] += this.vel[1];
		this.pos[0] += windSpeed * 0.0015;
		if (Date.now() - this.startTime > 15000) {
			powerups.delete(this.id);
		}
	}
}

const wss = new WebSocket.Server({
	port: parseInt(process.env.PORT, 10) || 3000
});
const players = new Map();
const powerups = new Map();

let seed = randint(0, 99999999);
let mode = "elimination";
let playerId = 0;
let powerupId = 0;
let waiting = true;

let windTime = Date.now();
let windDuration = randint(4000, 8000);
let windSpeed = [randint(-600, -200), randint(200, 600)][randint(0, 1)];

let powerupTime = Date.now();
let powerupDuration = randint(15000, 25000);

const totalTime = 60000;
let startTime, timerTime, midTime, elimTime;
let secondsLeft = totalTime;
let eliminated = 0;

wss.on("connection", (socket) => {
    const client = {
		id: playerId++,
		socket: socket
	};

	players.set(client.id, new Player(client));
	console.log(`Client ${client.id} connected`);
    socket.send_obj({"type": "hi", "id": client.id, "seed": seed, "waiting": waiting});

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
		if (players.has(client.id) && players.get(client.id).eliminated) return;

		if (msg.toString() === "admin") {
			handleAdminConnect(client);
			return;
		}

		if (client.id == -1) {
			handleAdminMessage(msg);
			return;
		}

		const strMsg = msg.toString();
		const data = JSON.parse(strMsg);
		if (data.type === "ir") {
			if (data.hit) {
				players.get(data.id).socket.send(strMsg);
			} else if (data.powerup) {
				powerups.delete(data.id);
			}
			return;
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
	playerId--;
}

function handleAdminMessage(msg) {
	const command = msg.toString();
	broadcast(JSON.stringify({"type": "ad", "command": command}));
	console.log(`Admin sent the command "${command}"`);
	if (command === "start") {
		waiting = false;
		timerTime = Date.now();
		startTime = Date.now();
		midTime = startTime + totalTime / 2;
		elimTime = totalTime / 2 / (players.size - 1 - 1); // minus admin, -1 again to offset the last two players
	} else if (command === "elimination") {
		mode = "elimination";
	} else if (command === "infinite") {
		mode = "infinite";
	} else if (command === "stop") {
		restart();
	}
}

function restart() {
	seed = randint(0, 99999999);
	startTime = Date.now();
	if (players.has(-1)) {
		let admin = players.get(-1);
		players.clear();
		players.set(-1, admin);
	}
	powerups.clear();
	waiting = true;
	eliminated = 0;
}

function game() {
	broadcastPlayerData();

	if (Date.now() - windTime > windDuration) {
		windTime = Date.now();
		windDuration = randint(3000, 6000);
		windSpeed = [randint(-600, -200), randint(200, 600)][randint(0, 1)];
		broadcast(JSON.stringify({"type": "wd", "speed": windSpeed}));
	}

	if (Date.now() - powerupTime > powerupDuration) {
		powerupTime = Date.now();
		powerupDuration = randint(15000, 25000);
		powerups.set(powerupId, new Powerup(powerupId));
	}
	for (const [id, powerup] of powerups) {
		powerup.update();
	}

	if (!waiting && mode === "elimination" && Date.now() - timerTime > 1000) {
		timerTime = Date.now();
		secondsLeft = Math.floor((totalTime - (Date.now() - startTime)) / 1000);
		broadcast(JSON.stringify({"type": "tm", "seconds": secondsLeft}));
		if (secondsLeft < 0) {
			restart();
		}
	}

	if (!waiting && !(players.size == 1 && players.has(-1)) && Date.now() - midTime > elimTime * (eliminated + 1)) {
		let min = 9999999;
		let min_player = null;
		for (const [id, player] of players) {
			if (id == -1 || player.eliminated) continue;
			if (player.data.score < min) {
				min = player.data.score;
				min_player = player;
			}
		}
		if (min_player !== null) {
			min_player.socket.send_obj({"type": "el"});
			min_player.eliminated = true;
			eliminated++;
		}
	}
}

setInterval(game, 12);