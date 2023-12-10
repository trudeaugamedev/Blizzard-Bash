const fs = require('fs');

function generateLeaderboardHTML() {
    const json_data = JSON.parse(fs.readFileSync('./leaderboard.json'));
    const playersWithScores = json_data.players.map(player => ({
        name: player,
        score: json_data.playersData[player].score
    }));

    playersWithScores.sort((a, b) => b.score - a.score);

    const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blizzard Bash Leaderboard</title>
    <link rel="stylesheet" href="index.css">
</head>
<body>
    <h1>Blizzard Bash Game Leaderboard</h1>
    <table>
        <tr>
            <th>Username</th>
            <th>Score</th>
        </tr>
        ${playersWithScores.map(player => `
        <tr>
            <td>${player.name}</td>
            <td>${player.score}</td>
        </tr>`).join('')}
    </table>
</body>
</html>`;

    fs.writeFileSync('./index.html', htmlContent);
}

generateLeaderboardHTML();

setInterval(() => {
    generateLeaderboardHTML();
}, 1000);
