# Risk
My implementation of a strategy board game Risk by Hasbro, Inc.

The official rules can be found here: https://www.ultraboardgames.com/risk/game-rules.php

The point of the game is to conquer all territories and eliminate all players. There are 4 players in the current version; however, it can be modified through game.py. Players have to take consequential turns on the same computer.

Installation:
- One option is to download all files, except the "lib" folder and the "game.exe" file. Then, execute the "game.py" file. Pygame is required for this option.
- Another way to play the game (only available on Windows) is to download the "lib" folder and the "game.exe" file and launch the latter. The executable was noticed to work slower than "game.py", so the first option is preferable.

Features:
- Blitz attack: attacker keeps rolling as many dice as one can until one conquers the territory or runs out of troops to attack with (thus having 1 troop remaining in the territory from which one is attacking). All of this is done instantaneously.
- Card bonus: to keep the game more balanced and focused on strategy rather than luck, card bonus is stable (4 for Infantry, 6 for Cavalry, 8 for Artillery, 10 for all three, plus territorial bonus).
- Automatic placement: Territories and the number of troops on each territories in the beginning are assigned at random.
- Privacy: to avoid seeing each other's cards, other players are not allowed to look at the screen until the current player is done with their turn.
