# Blizzard Bash - The Game

This is a multiplayer snowball fight game made for the 2022 Winter Carnival and the 2023 Blizzards Bash of Pierre Elliott Trudeau High School. 

### Version 1.0
Made for Winter Carnival, but it was never played due to an inclement weather day causing the cancelation of the event.

### Version 2.0
Made for Blizzards Bash, with significant graphics, mechanical, and backend upgrades. 

## Details
The client was written in Python using the Pygame framework, and the server is written in javascript, communication using websockets. 

It may be evident that the code is completely undocumented and an absolute mess of technical debt, but understand this was made under time constraints. 

This repository will be archived once Blizzards Bash is over, and the server will likely be closed down as well. It is licensed under the LGPL-2.1, please read [LICENSE](https://github.com/trudeaugamedev/Blizzard-Bash/blob/master/LICENSE) for more information on how you may use the contents of this repository. 

## Installation
If for whatever reason you wish to play the game after the event, you may follow the instructions below. Again, note that **the server will not be up after the even**t, so you would have to run the server locally using Node.js. 

### Windows
The game is built and distributed for Windows, download either version's executable by going under [Releases](https://github.com/trudeaugamedev/Blizzard-Bash/releases) and double click to run.

### Mac & Linux
No distribution is available. However, you may build from source.

### Building from source
Run the command `pyinstaller main.spec` in the root directory. It should then place the executable under `dist`.

Ensure you have Pyinstaller and Python installed, along with all the necessary python modules that I will not list here. 

### Running from source
If you have Python and the necessary modules installed, you may run `main.py` using Python. 

## Credits
- Programming by Andrew Wang
- Art by Richard Zhang
