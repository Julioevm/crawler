"""
Game map class for managing dungeon layout and entities.
"""

class GameMap:
    """Represents the game world map."""
    
    def __init__(self, width, height, ambient_light=0.1):
        self.width = width
        self.height = height
        self.tiles = [[0 for _ in range(width)] for _ in range(height)]
        self.entities = []
        self.ambient_light = ambient_light
        self.light_map = [[ambient_light for _ in range(width)] for _ in range(height)]
        
    def is_walkable(self, x, y):
        """Check if a tile is walkable (within bounds, not a wall, no blocking entity)."""
        # Check bounds
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
            
        # Check if it's a wall
        walkable_tiles = [0, 3]  # 0: floor, 3: open door
        if self.tiles[y][x] not in walkable_tiles:
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

    def update_light_map(self):
        """
        Update the light map based on light sources using a flood-fill (BFS) algorithm.
        """
        from collections import deque
        # Reset light map to ambient light
        self.light_map = [[self.ambient_light for _ in range(self.width)] for _ in range(self.height)]

        # Get all light sources
        light_sources = [entity for entity in self.entities if hasattr(entity, 'light_source') and entity.light_source]

        for source in light_sources:
            radius = source.light_source['radius']
            strength = source.light_source['strength']
            center_x, center_y = int(source.x), int(source.y)

            # Use BFS for light propagation
            queue = deque([(center_x, center_y, strength)])
            visited = set([(center_x, center_y)])

            self.light_map[center_y][center_x] = max(self.light_map[center_y][center_x], strength)

            while queue:
                x, y, light = queue.popleft()

                # Stop propagating if light is too dim
                if light <= self.ambient_light:
                    continue

                # Propagate to neighbors
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = x + dx, y + dy

                    if not (0 <= nx < self.width and 0 <= ny < self.height):
                        continue
                    
                    if (nx, ny) in visited:
                        continue
                    
                    distance = ((nx - center_x) ** 2 + (ny - center_y) ** 2) ** 0.5
                    if distance > radius:
                        continue

                    # Calculate new light value with falloff
                    ratio = distance / radius
                    falloff = 1.0 - ratio*ratio*(3.0 - 2.0*ratio) if ratio <= 1.0 else 0.0
                    new_light = strength * falloff

                    # Light up walls but don't propagate through them
                    if self.tiles[ny][nx] != 0:
                        if new_light > self.light_map[ny][nx]:
                            self.light_map[ny][nx] = new_light
                        continue # Stop propagation

                    visited.add((nx, ny))

                    if new_light > self.light_map[ny][nx]:
                        self.light_map[ny][nx] = new_light
                        queue.append((nx, ny, new_light))