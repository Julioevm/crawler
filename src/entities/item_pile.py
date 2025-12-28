"""
ItemPile entity class.
"""

from entities.entity import Entity

class ItemPile(Entity):
    """A pile of items on the ground."""

    def __init__(self, x, y, items=None):
        super().__init__(x, y, '*', "Items", "A pile of items on the ground.", sprite="item_pile")
        self.items = items if items is not None else []
        self.blocks_movement = False
        self.render_on_floor = True

    def interact(self, party):
        """Interact with the item pile."""
        return self.items

    def add_item(self, item):
        """Add an item to the pile."""
        self.items.append(item)

    def remove_item(self, item):
        """Remove an item from the pile."""
        if item in self.items:
            self.items.remove(item)