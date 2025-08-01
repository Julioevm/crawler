# Description

This project is a single player, first person dungeon crawler. Like Classic games Wizardry, Bards Tale, Eye of the Beholder.

Its turn-based, and the levels are based around a grid of cells.


## Setup

- We use UV to handle python verions and dependencies.
- Start the 'venv' before installing pip dependencies or running the main python script.

## Development

- Avoid using magic numbers, use variables and descriptive names. For reusable constants use the constants.py file.
- Be mindful of changes that might break existing code.
- Run the project after a change to ensure the game is working. `uv run src\main.py` Check the console for any error. Afterwards ask for player confirmation that the implementation was successful.
- We use Pygame and Pygame GUI, use these libraries as much as possible to avoid re-implementing some of its features.
- Check PROJECT_PLAN.md to check out completed features.
- Refer to project.md to check the design document for the game. If the changes conflict with it, prompt the user to confirm if we should update the design. Keep it in mind when developing to follow the expected gameplay.