"""
Chest entity class.
"""

from entities.entity import Entity

class Chest(Entity):
    """A chest that can contain items."""

    def __init__(self, x, y, items=None, trapped=False, locked=False):
        super().__init__(x, y, 'C', "Chest", "A container that might hold treasure.", sprite="chest")
        self.items = items if items is not None else []
        self.trapped = trapped
        self.locked = locked
        self.opened = False
        self.blocks_movement = False
        self.render_on_floor = True

    def interact(self, party):
        """Interact with the chest."""
        if self.locked:
            return "It's locked."
        if self.trapped:
            # Trigger trap
            self.trapped = False
            return "It was a trap!"
        
        self.opened = True
        self.blocks_movement = False
        return self.items

    def inspect(self, party):
        """Inspect the chest for traps."""
        if self.trapped:
            return "You found a trap!"
        else:
            return "You found no traps."

    def disarm(self, party):
        """Disarm a trap on the chest."""
        if self.trapped:
            self.trapped = False
            return "You disarmed the trap."
        else:
            return "There was no trap to disarm."

    def add_item(self, item):
        """Add an item to the chest."""
        self.items.append(item)

    def remove_item(self, item):
        """Remove an item from the chest."""
        if item in self.items:
            self.items.remove(item)