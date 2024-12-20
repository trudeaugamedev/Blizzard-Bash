# Blizzard Bash

This repository contains the source code for a multiplayer snowball fight game made for the 2022 Winter Carnival, 2023 Blizzards Bash and 2024 Game Dev Club's independent event at Pierre Elliott Trudeau High School.

# Details

The client was written in Python using the Pygame framework, and the server is written in javascript, communication using websockets.

It may be evident that the code is completely undocumented and an absolute mess of technical debt, but understand this was made under time constraints.

The server hosted on Heroku will be down after the event is over. To run it yourself, see [Installation](#installation).

# License

This project is licensed under the LGPL-2.1, please read [LICENSE](https://github.com/trudeaugamedev/Blizzard-Bash/blob/master/LICENSE) for more information on how you may use the contents of this repository.

# Versions

## Version 1.0

Made for Winter Carnival, but it was never played due to an inclement weather day causing the cancelation of the event.

## Version 2.0

Made for Blizzards Bash 2023, with significant graphics, mechanical, and backend upgrades.

## Version 3.0

Made for Game Dev Club's independent event in 2024, with tons of quality of life improvements and two new power-ups.

# Installation

If for whatever reason you wish to play the game after the event, you may follow the instructions below. Again, note that **the server will not be up after the event**, so you would have to run the server locally.

## Server

1. Install [Node.js](https://nodejs.org/en)
2. Clone this repository: `git clone https://github.com/trudeaugamedev/Blizzard-Bash.git`
3. `cd Blizzard-Bash`
4. `npm install`
5. `node server.js`

The server should now be started on `localhost:1200`.

## Client

**The distributions connect to the Heroku server which will not exist.**

### Windows

The game is built and distributed for Windows, download the executable by going under [Releases](https://github.com/trudeaugamedev/Blizzard-Bash/releases) and double click the executable to run.

### MacOS

GitHub actions for this repository generate build artifacts for MacOS.

### Linux

No distribution is available. However, you may run from source.

### Running from source

1. Dependency management of this repository is done with [Poetry](https://python-poetry.org/), either follow their installation instructions and initiate a Poetry project under this repository, OR install each dependency manually defined in `pyproject.toml`.
2. `python main.py` to run the client, make sure to modify the ip address under `client.py` according to your situation

# Building

Run `pyinstaller build.spec` and the resulting executable should appear under `dist/`.

# Credits
- Programming by Andrew Wang and Lucas Fu
- Art by Richard Zhang
- Programming help from Martin Baldwin
- Playtesting by our club members! ❤️
