"use strict";

// const WSS_URL = "ws://localhost:1200";
const WSS_URL = "wss://blizzard-bash-e8a3a44e5011.herokuapp.com";

// From https://stackoverflow.com/a/37388113
// draws an image with rotation + x/y flip + centering or not centering
function drawImage(img, x, y, width, height, deg, flip, flop, center) {
    ctx.save();

    if(typeof width === "undefined") width = img.width;
    if(typeof height === "undefined") height = img.height;
    if(typeof center === "undefined") center = false;

    // Set rotation point to center of image, instead of top/left
    if(center) {
        x -= width/2;
        y -= height/2;
    }

    // Set the origin to the center of the image
    ctx.translate(x + width/2, y + height/2);

    // Rotate the canvas around the origin
    let rad = 2 * Math.PI - deg * Math.PI / 180;
    ctx.rotate(rad);

    // Flip/flop the canvas
    let flipScale = flip ? -1 : 1;
    let flopScale = flop ? -1 : 1;
    ctx.scale(flipScale, flopScale);

    // Draw the image
    ctx.drawImage(img, -width/2, -height/2, width, height);

    ctx.restore();
}

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

// Fit canvas size to window
canvas.width = window.innerWidth - 30;
canvas.height = window.innerHeight - 30;
ctx.imageSmoothingEnabled = false;

let mousex = 0;
let dragging = false;

// Canvas drag event listeners
canvas.addEventListener("mousedown", (event) => {
    dragging = true;
    mousex = event.clientX;
});
canvas.addEventListener("touchstart", (event) => {
    dragging = true;
    mousex = event.touches[0].clientX;
})
canvas.addEventListener("mousemove", (event) => {
    if (!dragging) return;
    const dx = event.clientX - mousex;
    camera[0] -= dx * 0.5;
    mousex = event.clientX;
});
canvas.addEventListener("touchmove", (event) => {
    if (!dragging) return;
    const dx = event.touches[0].clientX - mousex;
    camera[0] -= dx * 0.5;
    mousex = event.touches[0].clientX;
});
canvas.addEventListener("mouseup", (event) => {
    dragging = false;
});
canvas.addEventListener("touchend", (event) => {
    dragging = false;
});

// Center the camera
let camera = [-canvas.width / 2, -canvas.height / 2];

// Load player images in the correct order
let playerPaths = [
    "../../assets/textures/player/player_idle_0.png",
    "../../assets/textures/player/player_idle_l_0.png",
    "../../assets/textures/player/player_idle_s_0.png",
    "../../assets/textures/player/player_dig_0.png",
    "../../assets/textures/player/player_dig_1.png",
    "../../assets/textures/player/player_dig_2.png",
    "../../assets/textures/player/player_dig_3.png",
    "../../assets/textures/player/player_dig_4.png",
    "../../assets/textures/player/player_dig_5.png",
    "../../assets/textures/player/player_dig_6.png",
    "../../assets/textures/player/player_dig_7.png",
    "../../assets/textures/player/player_dig_8.png",
    "../../assets/textures/player/player_dig_9.png",
    "../../assets/textures/player/player_run_0.png",
    "../../assets/textures/player/player_run_1.png",
    "../../assets/textures/player/player_run_2.png",
    "../../assets/textures/player/player_run_3.png",
    "../../assets/textures/player/player_run_4.png",
    "../../assets/textures/player/player_run_s_0.png",
    "../../assets/textures/player/player_run_s_1.png",
    "../../assets/textures/player/player_run_s_2.png",
    "../../assets/textures/player/player_run_s_3.png",
    "../../assets/textures/player/player_run_s_4.png",
    "../../assets/textures/player/player_run_l_0.png",
    "../../assets/textures/player/player_run_l_1.png",
    "../../assets/textures/player/player_run_l_2.png",
    "../../assets/textures/player/player_run_l_3.png",
    "../../assets/textures/player/player_run_l_4.png",
    "../../assets/textures/player/player_throw_l_0.png",
    "../../assets/textures/player/player_throw_l_1.png",
    "../../assets/textures/player/player_throw_l_2.png",
    "../../assets/textures/player/player_throw_l_3.png",
    "../../assets/textures/player/player_throw_s_0.png",
    "../../assets/textures/player/player_throw_s_1.png",
    "../../assets/textures/player/player_throw_s_2.png",
    "../../assets/textures/player/player_throw_s_3.png",
];
let playerImages = [];
for (let i = 0; i < playerPaths.length; i++) {
    playerImages.push(new Image());
    playerImages[i].src = playerPaths[i];
    playerImages[i].width *= 3;
    playerImages[i].height *= 3;
}

// Load snowball images
let smallSnowballImages = [];
for (let i = 0; i < 5; i++) {
    smallSnowballImages.push(new Image());
    smallSnowballImages[i].src = "../../assets/textures/snowball/snowball_small_" + i + ".png";
    smallSnowballImages[i].width *= 3;
    smallSnowballImages[i].height *= 3;
}
let largeSnowballImages = [];
for (let i = 0; i < 8; i++) {
    largeSnowballImages.push(new Image());
    largeSnowballImages[i].src = "../../assets/textures/snowball/snowball_large_" + i + ".png";
    largeSnowballImages[i].width *= 3;
    largeSnowballImages[i].height *= 3;
}

// Load powerup images
let rapidfire = new Image();
rapidfire.src = "../../assets/textures/powerup/rapidfire.png"
rapidfire.width *= 3
rapidfire.height *= 3
let strength = new Image();
strength.src = "../../assets/textures/powerup/strength.png"
strength.width *= 3
strength.height *= 3
let clustershot = new Image();
clustershot.src = "../../assets/textures/powerup/clustershot.png"
clustershot.width *= 3
clustershot.height *= 3

// Websocket events
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

// Textual display of the game state, for debug purposes
function displayGameState(data) {
    let strData = JSON.stringify(data, null, 3);
    document.getElementById("received").innerHTML = strData;
}

// Draw the game relative to the camera position according to the received game state
function drawGame(state) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (const p of state.players) {
        let image = playerImages[p.frame];
        drawImage(image, p.pos[0] - image.width / 2 - camera[0], p.pos[1] - image.height - camera[1], image.width, image.height, p.rot, p.flip, 0, true);

        for (const s of p.snowballs) {
            let image = (s.type == 0 ? smallSnowballImages : largeSnowballImages)[s.frame];
            drawImage(image, s.pos[0] - camera[0], s.pos[1] - camera[1], image.width, image.height, 0, 0, 0, true)
        }
    }

    // Since the server doesn't know where the ground is, the y pos of the powerup continues to move down
    for (const p of state.powerups) {
        let image = null;
        if (p.type === "rapidfire") {
            image = rapidfire;
        } else if (p.type === "strength") {
            image = strength;
        } else if (p.type === "clustershot") {
            image = clustershot;
        }
        drawImage(image, p.pos[0] - camera[0], p.pos[1] - camera[1], image.width, image.height, 0, 0, 0, true);
    }
}