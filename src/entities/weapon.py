"""
Weapon item class.
"""

from entities.item import Item

class Weapon(Item):
    """Weapon item that can be equipped by the player."""
    
    def __init__(self, name, description, attack_bonus):
        super().__init__(name, description, "weapon")
        self.attack_bonus = attack_bonus