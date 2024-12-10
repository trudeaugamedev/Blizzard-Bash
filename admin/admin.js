"use strict";

// const WSS_URL = "ws://localhost:1200";
const WSS_URL = "wss://blizzard-bash-e8a3a44e5011.herokuapp.com";

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
    let parsed = JSON.parse(event.data.toString());
    function deleteKey(obj, k) {
        for (let key in obj) {
            if (key === k) {
                delete obj[key];
            } else if (typeof obj[key] === "object") {
                deleteKey(obj[key], k);
            }
        }
    }

    hidden.forEach((key) => {
        deleteKey(parsed, key);
    });

    if (parsed.type === "cl") {
        displayGameState(parsed);
    }
});
socket.addEventListener("close", (event) => {
    document.getElementById("connectionStatus").textContent = "Disconnected, refresh to reconnect.";
    console.log("Websocket closed");
});

let toggles = [];
let hidden = [];

function getKeys(obj) {
    for (let key in obj) {
        if (!toggles.includes(key)) {
            toggles.push(key);
            document.getElementById("viewToggles").innerHTML += `<button class="toggle" id="toggle-${key}" onclick="toggleView('${key}')">${key}</button>`;
        }
        if (Array.isArray(obj[key])) {
            getKeys(obj[key][0]);
        } else if (typeof obj[key] === "object") {
            getKeys(obj[key]);
        }
    }
}

function displayGameState(data) {
    data = JSON.stringify(data, null, 3);
    document.getElementById("received").innerHTML = data;

    getKeys(JSON.parse(data.toString()));
}

function toggleView(key) {
    if (hidden.includes(key)) {
        hidden.splice(hidden.indexOf(key), 1);
        document.getElementById(`toggle-${key}`).classList.remove("hidden");
    } else {
        hidden.push(key);
        document.getElementById(`toggle-${key}`).classList.add("hidden");
    }
}

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