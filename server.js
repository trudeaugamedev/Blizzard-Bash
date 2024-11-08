const WebSocket = require("ws");
const fs = require("fs");

function randint(min, max) {
	return Math.floor(Math.random() * (max - min + 1)) + min;
}

function broadcast(msg) {
	for (const player of players.values()) {
		player.socket.send(msg);
	}
	for (const spectator of spectators.values()) {
		spectator.socket.send(msg);
	}
}

function getPlayerData(x_id, init) {
	let playerDataArray = [];
	for (const [id, player] of players) {
		if (id === x_id) continue;
		if (id === -1) continue;
		if (player.eliminated) continue;
		if (player.sent == players.size - 1 && !init) continue;
		if (player.received.id == -2) continue; // assuming it might be delay, but -2 is when the player hasn't gotten an id yet
		playerDataArray.push(init ? player.data : player.received);
		player.sent++;
	}

	let powerupDataArray = Array.from(powerups.values()).map(powerup => ({
		"id": powerup.id,
		"type": powerup.type,
		"pos": [Math.floor(powerup.pos[0]), Math.floor(powerup.pos[1])],
	}));

	return {
		"type": "cl",
		"players": playerDataArray,
		"powerups": powerupDataArray,
	};
}

function broadcastPlayerData() {
	for (const [id, player] of players) {
		player.socket.send(JSON.stringify(getPlayerData(id, id === -1)));
	}
	for (const [id, spectator] of spectators) {
		spectator.socket.send(JSON.stringify(getPlayerData(-1, true)));
	}
}

WebSocket.WebSocket.prototype.send_obj = function send_obj (obj) {
	this.send(JSON.stringify(obj));
}

class Player {
	constructor (client) {
		this.id = client.id;
		this.socket = client.socket;
		this.data = {};
		this.received = {};
		// the number of other players it has already sent the received data out to before a new update
		this.sent = 0;
		this.eliminated = false;
	}
}

class Powerup {
	constructor (id) {
		this.id = id;
		powerupId++;
		this.vel = [0, 0]
		this.pos = [randint(-2400, 2400), -1200];
		this.type = ["rapidfire", "strength", "clustershot", "hailstorm"][randint(0, 3)];
		this.startTime = Date.now();
	}

	update() {
		this.vel[1] += 0.01;
		this.pos[1] += this.vel[1];
		this.pos[0] += windSpeed * 0.0015;
		if (Date.now() - this.startTime > 20000) {
			powerups.delete(this.id);
		}
	}
}

const wss = new WebSocket.Server({
	port: parseInt(process.env.PORT, 10) || 1200
});
const players = new Map();
const spectators = new Map();
const powerups = new Map();

let seed = randint(0, 99999999);
let mode = "elimination";
let playerId = 0;
let spectatorId = 0;
let powerupId = 0;
let waiting = true;

let windTime = Date.now();
let windDuration = randint(4000, 8000);
let windSpeed = [randint(-600, -200), randint(200, 600)][randint(0, 1)];

let powerupTime = Date.now();
let powerupDuration = randint(5000, 15000);

let totalTime = 600000;
let startTime, timerTime, midTime, elimTime;
let secondsLeft = totalTime;
let eliminated = 0;

wss.on("connection", (socket) => {
    const client = {
		id: playerId++,
		socket: socket
	};

	if (waiting) broadcast(JSON.stringify({"type": "cn", "id": client.id}));

    socket.send_obj({"type": "hi", "id": client.id, "seed": seed, "waiting": waiting, "data": getPlayerData(client.id, true)});
	players.set(client.id, new Player(client));
	console.log(`Client ${client.id} connected`);

	if (!waiting) players.get(client.id).eliminated = true;

	socket.on("error", (error) => {
		console.error(error);
	});

	socket.on("close", (code) => {
		players.delete(client.id);
		socket.close();
		if (client.id === -1) {
			console.log(`Admin has disconnected, code ${code}`);
		} else {
			console.log(`Client ${client.id} disconnected, code ${code}`);
		}
		broadcast(JSON.stringify({"type": "dc", "id": client.id}));
	});

	socket.on("message", (msg) => {
		if (players.has(client.id) && players.get(client.id).eliminated) {
			// set player name and score only
			const strMsg = msg.toString();
			let data = "";
			try {
				data = JSON.parse(strMsg);
			} catch (err) {
				return;
			}
			let playerData = players.get(client.id).data;
			for (const [key, value] of Object.entries(data)) {
				if (value === null) continue;
				if (!(key === "name" || key === "score")) continue;
				playerData[key] = value;
			}
			return;
		}

		if (msg.toString() === "admin") {
			handleAdminConnect(client);
			return;
		} else if (msg.toString() === "spectator") {
			handleSpectatorConnect(client);
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

		if (!players.has(client.id)) return;
		players.get(client.id).received = data;
		players.get(client.id).sent = 0;
		let playerData = players.get(client.id).data;
		for (const [key, value] of Object.entries(data)) {
			if (value === null) continue;
			playerData[key] = value;
		}
	});
});

function handleAdminConnect(client) {
	console.log("Admin has connected");
	broadcast(JSON.stringify({"type": "dc", "id": client.id}));
	// Move the admin player object to -1, since it was added as a normal player on connection
	players.set(-1, players.get(client.id));
	players.delete(client.id);
	// Change IDs
	players.get(-1).id = -1;
	client.id = -1;
	playerId--;
}

function handleSpectatorConnect(client) {
	console.log("A spectator has connected");
	broadcast(JSON.stringify({"type": "dc", "id": client.id}));
	spectators.set(spectatorId++, client);
	players.delete(client.id);
}

function handleAdminMessage(msg) {
	const command = msg.toString();
	broadcast(JSON.stringify({"type": "ad", "command": command}));
	console.log(`Admin sent the command "${command}"`);
	if (command.startsWith("start")) {
		let minutes = command.substring(6);
		if (minutes) {
			totalTime = parseFloat(minutes) * 60000;
		}
		waiting = false;
		timerTime = Date.now();
		startTime = Date.now();
		midTime = startTime + totalTime / 2;
		elimTime = totalTime / 2 / (players.size - 1 - 1); // minus admin, -1 again to offset the last two players
		secondsLeft = Math.floor((totalTime - (Date.now() - startTime)) / 1000) - 1;
		broadcast(JSON.stringify({"type": "tm", "seconds": secondsLeft}));
	} else if (command === "elimination") {
		mode = "elimination";
	} else if (command === "infinite") {
		mode = "infinite";
	} else if (command === "stop") {
		let scoreData = [];
		for (const [id, player] of players) {
			if (id === -1) continue;
			scoreData.push({"id": id, "name": player.data.name, "score": player.data.score});
		}
		broadcast(JSON.stringify({"type": "en", "data": scoreData}));
		restart();
	} else if (command.startsWith("kick")) {
		let id = parseInt(command.substring(5));
		if (players.has(id)) {
			players.get(id).socket.send_obj({"type": "kc"});
			players.delete(id);
			broadcast(JSON.stringify({"type": "dc", "id": id}));
		} else {
			console.log(`Non-existent player id ${id}!`)
		}
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
		powerupDuration = randint(5000, 15000);
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
			let scoreData = [];
			for (const [id, player] of players) {
				if (id === -1) continue;
				scoreData.push({"id": id, "name": player.data.name, "score": player.data.score});
			}
			broadcast(JSON.stringify({"type": "en", "data": scoreData}));
			restart();
		}
	}

	if (!waiting && !(players.size == 1 && players.has(-1)) && Date.now() - midTime > elimTime * (eliminated + 1)) {
		let min = 99999;
		for (const [id, player] of players) {
			if (id == -1 || player.eliminated) continue;
			if (player.data.score < min) {
				min = player.data.score;
			}
		}
		if (min !== 99999) {
			let choices = [];
			for (const [id, player] of players) {
				if (player.data.score !== min) continue;
				choices.push(player);
			}
			if (choices.length > 0) {
				let min_player = choices.at(randint(0, choices.length - 1));
				min_player.socket.send_obj({"type": "el"});
				min_player.eliminated = true;
				eliminated++;
				broadcast(JSON.stringify({"type": "dc", "id": min_player.id}));
				console.log(`Eliminated player '${min_player.data.name}' at id ${min_player.id}`);
			}
		}
	}
}

setInterval(game, 12);
