"""
Simple AI for enemy entities.
"""

import random

class BasicAI:
    """Basic AI for enemy entities."""
    
    def __init__(self, entity):
        self.entity = entity
        
    def take_turn(self, game_map):
        """Take a turn for the entity."""
        # Simple AI: randomly move in one of the four directions or stay still
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (0, 0)]  # Include staying still
        dx, dy = random.choice(directions)
        
        # Try to move in the chosen direction
        new_x = int(self.entity.x) + dx
        new_y = int(self.entity.y) + dy
        
        # Check if the new position is valid and not occupied by another entity
        if game_map.is_walkable(new_x, new_y):
            # Check if there's no other entity in the target position
            entities_at_target = game_map.get_entities_at(new_x, new_y)
            if not entities_at_target:
                self.entity.x = new_x
                self.entity.y = new_y