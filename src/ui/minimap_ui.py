"""
Minimap UI component for displaying the game map.
"""

import pygame

class MinimapUI:
    """Minimap UI component for the game."""
    
    def __init__(self, screen_width, screen_height, map_width, map_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_width = map_width
        self.map_height = map_height
        self.visible = False
        self.tile_size = 20  # Size of each tile in pixels on the minimap
        self.padding = 20    # Padding around the minimap
        
        # Calculate the size of the minimap surface
        self.minimap_width = self.map_width * self.tile_size
        self.minimap_height = self.map_height * self.tile_size
        
        # Create the minimap surface
        self.minimap_surface = pygame.Surface((self.minimap_width, self.minimap_height))
        
        # Colors
        self.wall_color = (100, 100, 100)      # Gray for walls
        self.floor_color = (50, 50, 50)        # Dark gray for floors
        self.player_color = (0, 255, 0)        # Green for player
        self.enemy_color = (255, 0, 0)         # Red for enemies
        self.item_color = (255, 255, 0)        # Yellow for items
        self.background_color = (30, 30, 30)   # Dark background
        
    def toggle_visibility(self):
        """Toggle the visibility of the minimap."""
        self.visible = not self.visible
        
    def handle_input(self, event):
        """Handle input events for the minimap."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.toggle_visibility()
                return True
        return False
        
    def draw(self, screen, game_map, player):
        """Draw the minimap on the screen."""
        if not self.visible:
            return
            
        # Clear the minimap surface
        self.minimap_surface.fill(self.background_color)
        
        # Draw the map tiles
        for y in range(self.map_height):
            for x in range(self.map_width):
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, 
                                   self.tile_size, self.tile_size)
                if game_map.tiles[y][x] == 1:  # Wall
                    pygame.draw.rect(self.minimap_surface, self.wall_color, rect)
                else:  # Floor
                    pygame.draw.rect(self.minimap_surface, self.floor_color, rect)
                    
                # Draw grid lines
                pygame.draw.rect(self.minimap_surface, (70, 70, 70), rect, 1)
        
        # Draw entities
        for entity in game_map.entities:
            if hasattr(entity, 'x') and hasattr(entity, 'y'):
                # Determine color based on entity type
                color = self.item_color
                if hasattr(entity, 'is_alive') and entity.is_alive():
                    color = self.enemy_color
                elif entity == player:
                    color = self.player_color
                    
                # Draw the entity
                center_x = int(entity.x) * self.tile_size + self.tile_size // 2
                center_y = int(entity.y) * self.tile_size + self.tile_size // 2
                pygame.draw.circle(self.minimap_surface, color, (center_x, center_y), self.tile_size // 3)
                
                # Draw player direction indicator
                if entity == player:
                    # Calculate the end point of the direction indicator
                    dir_length = self.tile_size // 2
                    end_x = center_x + int(dir_length * pygame.math.Vector2(1, 0).rotate_rad(player.angle).x)
                    end_y = center_y + int(dir_length * pygame.math.Vector2(1, 0).rotate_rad(player.angle).y)
                    pygame.draw.line(self.minimap_surface, (255, 255, 255), (center_x, center_y), (end_x, end_y), 2)
        
        # Create a background surface for the minimap with padding
        bg_width = self.minimap_width + 2 * self.padding
        bg_height = self.minimap_height + 2 * self.padding
        bg_surface = pygame.Surface((bg_width, bg_height))
        bg_surface.fill((0, 0, 0))
        pygame.draw.rect(bg_surface, (100, 100, 100), (0, 0, bg_width, bg_height), 2)
        
        # Blit the minimap onto the background surface
        bg_surface.blit(self.minimap_surface, (self.padding, self.padding))
        
        # Position the minimap in the center of the screen
        x_pos = (self.screen_width - bg_width) // 2
        y_pos = (self.screen_height - bg_height) // 2
        
        # Draw the minimap background surface on the screen
        screen.blit(bg_surface, (x_pos, y_pos))
        
        # Draw a title
        font = pygame.font.Font(None, 36)
        title = font.render("Minimap - Press TAB to close", True, (255, 255, 255))
        title_x = (self.screen_width - title.get_width()) // 2
        screen.blit(title, (title_x, y_pos - 40))