// const WSS_URL = "ws://localhost:1200";
const WSS_URL = "wss://blizzard-bash-e8a3a44e5011.herokuapp.com";

const socket = new WebSocket(WSS_URL);
socket.addEventListener("error", (event) => {
    console.error("Websocket error: ", event);
});
socket.addEventListener("open", (event) => {
    console.log(`Websocket started on ${WSS_URL}`);
    socket.send("leaderboard");
    socket.send("updatelb");
});
socket.addEventListener("message", (event) => {
    let players = JSON.parse(event.data.toString());
    if (!Array.isArray(players)) return;
    console.log(players);

    players.sort((a, b) => b.score - a.score);

    const tbody = document.querySelector('table tbody');
    tbody.innerHTML = players.map(player => player.name != null ? `
        <tr>
            <td>${player.name}</td>
            <td>${player.score}</td>
        </tr>
    ` : "").join('');
});
socket.addEventListener("close", (event) => {
    console.log("Websocket closed");
});

setInterval(() => {
    socket.send("updatelb");
}, 5000);