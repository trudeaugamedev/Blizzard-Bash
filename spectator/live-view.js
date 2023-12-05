"use strict";

// const WSS_URL = "ws://localhost:3000";
const WSS_URL = "wss://trudeaugamedev-winter.herokuapp.com";

function flip(ctx, image, x, y, horizontal, vertical){
    ctx.save();
    ctx.scale(horizontal, vertical);
    ctx.drawImage(image, horizontal * x, vertical * y, horizontal * image.width, vertical * image.height);
    ctx.restore();
}

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth - 30;
canvas.height = window.innerHeight - 30;
ctx.imageSmoothingEnabled = false;

let mousex = 0;
let dragging = false;

canvas.addEventListener("mousedown", (event) => {
    dragging = true;
    mousex = event.clientX;
});
canvas.addEventListener("mousemove", (event) => {
    if (!dragging) return;
    const dx = event.clientX - mousex;
    camera[0] -= dx * 0.5;
    mousex = event.clientX;
});
canvas.addEventListener("mouseup", (event) => {
    dragging = false;
});

let camera = [-canvas.width / 2, -canvas.height / 2];

let player_paths = [
    "../assets/textures/player/player_idle_0.png",
    "../assets/textures/player/player_idle_l_0.png",
    "../assets/textures/player/player_idle_s_0.png",
    "../assets/textures/player/player_dig_0.png",
    "../assets/textures/player/player_dig_1.png",
    "../assets/textures/player/player_dig_2.png",
    "../assets/textures/player/player_dig_3.png",
    "../assets/textures/player/player_dig_4.png",
    "../assets/textures/player/player_dig_5.png",
    "../assets/textures/player/player_dig_6.png",
    "../assets/textures/player/player_dig_7.png",
    "../assets/textures/player/player_dig_8.png",
    "../assets/textures/player/player_dig_9.png",
    "../assets/textures/player/player_run_0.png",
    "../assets/textures/player/player_run_1.png",
    "../assets/textures/player/player_run_2.png",
    "../assets/textures/player/player_run_3.png",
    "../assets/textures/player/player_run_4.png",
    "../assets/textures/player/player_run_s_0.png",
    "../assets/textures/player/player_run_s_1.png",
    "../assets/textures/player/player_run_s_2.png",
    "../assets/textures/player/player_run_s_3.png",
    "../assets/textures/player/player_run_s_4.png",
    "../assets/textures/player/player_run_l_0.png",
    "../assets/textures/player/player_run_l_1.png",
    "../assets/textures/player/player_run_l_2.png",
    "../assets/textures/player/player_run_l_3.png",
    "../assets/textures/player/player_run_l_4.png",
    "../assets/textures/player/player_throw_l_0.png",
    "../assets/textures/player/player_throw_l_1.png",
    "../assets/textures/player/player_throw_l_2.png",
    "../assets/textures/player/player_throw_l_3.png",
    "../assets/textures/player/player_throw_s_0.png",
    "../assets/textures/player/player_throw_s_1.png",
    "../assets/textures/player/player_throw_s_2.png",
    "../assets/textures/player/player_throw_s_3.png",
];
let player_images = [];
for (let i = 0; i < player_paths.length; i++) {
    player_images.push(new Image());
    player_images[i].src = player_paths[i];
    player_images[i].width *= 3;
    player_images[i].height *= 3;
}

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

function drawGame(state) {
    console.log("lmao :(");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (const p of state.players) {
        let image = player_images[p.frame];
        flip(ctx, image, p.pos[0] - image.width / 2 - camera[0], p.pos[1] - image.height - camera[1], 1, 0);
    }
}