"""
Potion item class.
"""

from entities.item import Item

class Potion(Item):
    """Potion item that can heal the player."""
    
    def __init__(self, name, description, heal_amount):
        super().__init__(name, description, "potion")
        self.heal_amount = heal_amount
        
    def use(self, player):
        """Use the potion to heal the player."""
        player.heal(self.heal_amount)
        return f"You drink the {self.name} and recover {self.heal_amount} HP."