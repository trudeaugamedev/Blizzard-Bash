
function generateLeaderboardHTML() {
    readTextFile('leaderboard.json', function (json_data) {
        const playersWithScores = json_data.players.map(player => ({
            name: player,
            score: json_data.playersData[player]
        }));

        playersWithScores.sort((a, b) => b.score - a.score);

        const tbody = document.querySelector('table tbody');
        tbody.innerHTML = playersWithScores.map(player => player.name != null ? `
            <tr>
                <td>${player.name}</td>
                <td>${player.score}</td>
            </tr>
        ` : "").join('');
    });
}

function readTextFile(fileName, callback) {
    const xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);
            callback(data);
        }
    };
    xhr.open('GET', fileName, true);
    xhr.send();
}

generateLeaderboardHTML();

setInterval(generateLeaderboardHTML, 1000);