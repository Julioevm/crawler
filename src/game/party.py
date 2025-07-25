"""
Party class for managing the player's characters.
"""

import math
from entities.entity import Entity

class Party(Entity):
    """Represents the player's party."""

    def __init__(self, x, y):
        super().__init__(x, y, '@', "Party", "A group of adventurers.", light_source={'radius': 8, 'strength': 1.0})
        self.characters = []
        self.inventory = []
        self.facing = 0  # 0=north, 1=east, 2=south, 3=west
        self.angle = 0.0  # 0 = north, π/2 = east, π = south, 3π/2 = west

    def add_character(self, character):
        """Add a character to the party."""
        self.characters.append(character)

    def turn_left(self):
        """Turn the party 90 degrees counter-clockwise."""
        self.facing = (self.facing - 1) % 4
        self.angle = self.facing * (math.pi / 2)

    def turn_right(self):
        """Turn the party 90 degrees clockwise."""
        self.facing = (self.facing + 1) % 4
        self.angle = self.facing * (math.pi / 2)

    def gain_xp(self, amount):
        """Give XP to all characters in the party."""
        for character in self.characters:
            character.gain_xp(amount)

    def add_to_inventory(self, item):
        """Add an item to the party's inventory."""
        self.inventory.append(item)

    def remove_from_inventory(self, item):
        """Remove an item from the party's inventory."""
        if item in self.inventory:
            self.inventory.remove(item)

    def is_alive(self):
        """Check if any character in the party is alive."""
        return any(c.hp > 0 for c in self.characters)