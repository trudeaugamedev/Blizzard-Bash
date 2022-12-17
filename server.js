const { WebSocketServer } = require("ws");

function randint(min, max) {
	return Math.floor(Math.random() * (max - min + 1)) + min;
}

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

const seed = randint(0, 99999999)
var wind_time = Date.now();
var wind_duration = randint(3000, 6000);
var wind_speed = [randint(-600, -200), randint(200, 600)][randint(0, 1)];

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
		if (Date.now() - wind_time > wind_duration) {
			wind_time = Date.now();
			wind_duration = randint(3000, 6000);
			wind_speed = [randint(-600, -200), randint(200, 600)][randint(0, 1)];
			broadcast(`wd ${wind_speed}`);
		}
	});

	socket.send(`hi ${seed}`);
});