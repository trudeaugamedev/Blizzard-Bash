function generateLeaderboardHTML() {
    fetch("http://127.0.0.1:3001").then((response) => {
    // fetch("wss://trudeaugamedev-winter.herokuapp.com").then((response) => {
        return response.json();
    }).then((data) => {
        console.log(data);
        const players = Object.values(data);

        players.sort((a, b) => b.score - a.score);

        const tbody = document.querySelector('table tbody');
        tbody.innerHTML = players.map(player => player.name != null ? `
            <tr>
                <td>${player.name}</td>
                <td>${player.score}</td>
            </tr>
        ` : "").join('');
    }).catch((err) => {
        console.log("Fetch Error!", err);
    });

    /*`<tr>
        <td>${player.name}</td>
        <td>${player.score}</td>
    </tr>`*/
}

generateLeaderboardHTML();

setInterval(generateLeaderboardHTML, 5000);