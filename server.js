const { WebSocketServer } = require("ws");

function randint(min, max) {
	return Math.floor(Math.random() * (max - min + 1)) + min;
}

let nextid = 0;

const wss = new WebSocketServer({
	port: parseInt(process.env.PORT, 10) || 3000,
});

const clients = new Map();
const ready = new Map();

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

const total_time = 30000;
const total_time_s = total_time / 1000;

let seed = randint(0, 99999999);
let game_start = Date.now();
let started = false;
let total_players = 0;
let eliminations = 0;

let wind_time = Date.now();
let wind_duration = randint(3000, 6000);
let wind_speed = [randint(-600, -200), randint(200, 600)][randint(0, 1)];

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
		ready.delete(client.id);
		socket.close();
		console.log(`Client ${client.id} disconnected, code ${code}`);
		broadcast(`dc ${client.id}`);
	});

	socket.on("message", (msg) => {
		if ((started && Date.now() - game_start > total_time / total_players * (eliminations + 2)) || (started && clients.size == 1)) {
			eliminations += 1;
			if (clients.size > 2 || Date.now() - game_start >= total_time) {
				broadcast(`el`); // Eliminate
			}
			if (clients.size <= 1) {
				seed = randint(0, 99999999);
				started = false;
				eliminations = 0;
				total_players = 0;
				nextid = 0;
				clients.clear();
			}
			return;
		}

		ready.set(client.id, parseInt(msg.toString()[msg.length - 1]));
		if (Array.from(ready.values()).every(element => element === 1) && !started && clients.size > 1) {
			game_start = Date.now();
			started = true;
			total_players = clients.size;
			console.log(`Everyone is ready!`);
			broadcast("rd");
		}

		if (started) {
			if (client.size > 2) {
				broadcast(`tm ${parseInt(total_time_s - (Date.now() - game_start) / 1000)} ${parseInt((total_time / total_players * (eliminations + 2) - (Date.now() - game_start)) / 1000)}`);
			} else {
				broadcast(`tm ${parseInt(total_time_s - (Date.now() - game_start) / 1000)} ${parseInt(total_time_s - (Date.now() - game_start) / 1000)}`);
			}
		}

		xbroadcast(client.id, `cl ${client.id} ${msg}`);

		if (Date.now() - wind_time > wind_duration) {
			wind_time = Date.now();
			wind_duration = randint(3000, 6000);
			wind_speed = [randint(-600, -200), randint(200, 600)][randint(0, 1)];
			broadcast(`wd ${wind_speed}`);
		}
	});

	socket.send(`hi ${client.id} ${seed}`);
	ready.set(client.id, 0)
	if (started && clients.size > 0) {
		socket.close();
		console.log(`Client ${client.id} tried to join during a game.`);
	}
});