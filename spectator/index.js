"use strict";

const WSS_URL = "ws://localhost:3000";
// const WSS_URL = "wss://trudeaugamedev-winter.herokuapp.com";

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
    }
});
socket.addEventListener("close", (event) => {
    document.getElementById("connectionStatus").textContent = "Disconnected, refresh to reconnect.";
    console.log("Websocket closed");
});

function displayGameState(data) {
    data = JSON.stringify(data, null, 3);
    document.getElementById("received").innerHTML = data;
}