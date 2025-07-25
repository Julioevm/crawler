"""
Base entity class for all game objects.
"""

class Entity:
    """Base class for all entities in the game world."""
    
    def __init__(self, x, y, symbol, name, description="", sprite=None, light_source=None):
        self.x = x
        self.y = y
        self.symbol = symbol  # Character used to represent the entity on map
        self.name = name
        self.description = description
        self.sprite = sprite
        self.blocks_movement = True  # By default, entities block movement
        self.light_source = light_source
    
    def move(self, dx, dy, game_map):
        """Attempt to move the entity by dx, dy on the game map."""
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check if the new position is valid
        if game_map.is_walkable(new_x, new_y):
            self.x = new_x
            self.y = new_y
            return True
        return False
    
    def distance_to(self, other):
        """Calculate the Manhattan distance to another entity."""
        return abs(self.x - other.x) + abs(self.y - other.y)
        
    def is_alive(self):
        """Check if the entity is alive (by default, entities are always alive)."""
        return True