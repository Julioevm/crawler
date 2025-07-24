"""
Item class for game items.
"""

class Item:
    """Base class for all items in the game."""
    
    def __init__(self, name, description, item_type="misc"):
        self.name = name
        self.description = description
        self.item_type = item_type  # e.g., "weapon", "armor", "potion", "misc"
        
    def use(self, player):
        """Use the item (to be overridden by subclasses)."""
        pass