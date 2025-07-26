# Description

This project is a single player, first person dungeon crawler. Like Classic games Wizardry, Bards Tale, Eye of the Beholder.

Its turn-based, and the levels are based around a grid of cells.


## Setup

- We use UV to handle python verions and dependencies.
- Start the 'venv' before installing pip dependencies or running the main python script.

## Development

- Avoid using magic numbers, use variables and descriptive names. For reusable contants use the constants.py file.
- Be mindful of changes that might break existing code.
- Run the project after a change to ensure the game is working. `uv run src\main.py`
- We use Pygame and Pygame GUI, use these libraries as possible.