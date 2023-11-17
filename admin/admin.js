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
    socket.send("admin");
});
socket.addEventListener("message", (event) => {
    if (JSON.parse(event.data.toString()).type === "cl") return;
    document.getElementById("received").innerHTML = event.data + "<br>" + document.getElementById("received").innerHTML;
});
socket.addEventListener("close", (event) => {
    document.getElementById("connectionStatus").textContent = "Disconnected, refresh to reconnect.";
    console.log("Websocket closed");
});

function sendCommand() {
    let command = document.getElementById("commandPrompt").value;
    socket.send(command);
    document.getElementById("commands").innerHTML = command + "<br>" + document.getElementById("commands").innerHTML;
}

let commandPrompt = document.getElementById("commandPrompt");
commandPrompt.addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
        document.getElementById("sendCommand").click();
    }
});