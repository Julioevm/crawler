# Description

This project is a single player, first person dungeon crawler. Like Classic games Wizardry, Eye of the Beholder.

## Gameplay

Its turn-based, and the levels are based around a grid of cells.

The player controls a party of characters.

Enemies encountered patrolling the dungeons might be alone or a group of multiple enemies.

There will be chests, traps and other interactive elements in the map.

### Combat

Each turn your party trades blows with the enemies in the opposing party.

WIP

### Inventory

The whole party shares a common inventory.
Each character in the party can equip or use equipment separately.


## Setup

- We use UV to handle python versions and dependencies.
- Start the 'venv' before installing pip dependencies or running the main python script.

## Development

- Avoid using magic numbers, use variables and descriptive names.
- Be mindful of changes that might break existing code.
- Run the project after a change to ensure the game is working.

### Debug

- Run with `--fps` argument to see the FPS counter in-game.