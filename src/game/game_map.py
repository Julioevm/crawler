"""
Game map class for managing dungeon layout and entities.
"""

class GameMap:
    """Represents the game world map."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[0 for _ in range(width)] for _ in range(height)]
        self.entities = []
        
    def is_walkable(self, x, y):
        """Check if a tile is walkable (within bounds, not a wall, no blocking entity)."""
        # Check bounds
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
            
        # Check if it's a wall
        if self.tiles[y][x] != 0:
            return False
            
        # Check for blocking entities
        for entity in self.entities:
            if int(entity.x) == x and int(entity.y) == y and entity.blocks_movement:
                return False
                
        return True
        
    def add_entity(self, entity):
        """Add an entity to the map."""
        self.entities.append(entity)
        
    def remove_entity(self, entity):
        """Remove an entity from the map."""
        if entity in self.entities:
            self.entities.remove(entity)
            
    def get_entities_at(self, x, y):
        """Get all entities at a specific position."""
        return [entity for entity in self.entities if int(entity.x) == x and int(entity.y) == y]
        
    def get_blocking_entities_at(self, x, y):
        """Get all blocking entities at a specific position."""
        return [entity for entity in self.entities 
                if int(entity.x) == x and int(entity.y) == y and entity.blocks_movement]
                
    def move_entity(self, entity, dx, dy):
        """Move an entity by dx, dy in grid coordinates."""
        new_x = int(entity.x) + dx
        new_y = int(entity.y) + dy
        
        # Check if the new position is valid
        if self.is_walkable(new_x, new_y):
            entity.x = new_x
            entity.y = new_y
            return True
        return False