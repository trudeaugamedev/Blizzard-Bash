"use strict";

const WSS_URL = "ws://localhost:3000";
// const WSS_URL = "wss://trudeaugamedev-winter.herokuapp.com";

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

let mouse = [0, 0];
let dragging = false;

canvas.addEventListener("mousedown", (event) => {
    dragging = true;
    mouse[0] = event.clientX;
    mouse[1] = event.clientY;
});
canvas.addEventListener("mousemove", (event) => {
    if (!dragging) return;
    const delta = [event.clientX - mouse[0], event.clientY - mouse[1]];
    camera[0] -= delta[0] * 0.5;
    camera[1] -= delta[1] * 0.5;
    mouse[0] = event.clientX;
    mouse[1] = event.clientY;
});
canvas.addEventListener("mouseup", (event) => {
    dragging = false;
});

let camera = [-100, -100];

const player = new Image();
player.src = "../assets/textures/player/player_idle_0.png";

const socket = new WebSocket(WSS_URL);
socket.addEventListener("error", (event) => {
    console.error("Websocket error: ", event);
});
socket.addEventListener("open", (event) => {
    console.log(`Websocket started on ${WSS_URL}`);
    document.getElementById("connectionStatus").textContent = `Connected to ${WSS_URL}`;
    socket.send("spectator");
});
socket.addEventListener("message", (event) => {
    let parsed = JSON.parse(event.data.toString());
    if (parsed.type === "cl") {
        displayGameState(parsed);
        drawGame(parsed);
    }
});
socket.addEventListener("close", (event) => {
    document.getElementById("connectionStatus").textContent = "Disconnected, refresh to reconnect.";
    console.log("Websocket closed");
});

function displayGameState(data) {
    let str_data = JSON.stringify(data, null, 3);
    document.getElementById("received").innerHTML = str_data;
}

function drawGame(data) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (const p of data.players) {
        ctx.drawImage(player, p.pos[0] - camera[0], p.pos[1] - camera[1]);
    }
}