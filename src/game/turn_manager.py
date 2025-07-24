"""
Turn manager for handling turn-based gameplay.
"""

class TurnManager:
    """Manages the turn-based gameplay flow."""
    
    def __init__(self, game_map):
        self.game_map = game_map
        self.player_turn = True
        self.turn_number = 1
        
    def end_player_turn(self):
        """End the player's turn and start enemy turns."""
        self.player_turn = False
        self.process_enemy_turns()
        self.player_turn = True
        self.turn_number += 1
        
    def process_enemy_turns(self):
        """Process all enemy actions for the current turn."""
        # Create a copy of the entities list to avoid modification during iteration
        entities_copy = list(self.game_map.entities)
        
        for entity in entities_copy:
            # Process turns for enemies (entities with AI)
            if hasattr(entity, 'ai') and entity.ai and entity.is_alive():
                entity.ai.take_turn(self.game_map)