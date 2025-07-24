"""
Inventory UI for displaying and managing player items.
"""

import pygame

class InventoryUI:
    """UI for displaying and managing the player's inventory."""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 24)
        self.visible = False
        self.selected_item = 0
        
    def toggle_visibility(self):
        """Toggle the visibility of the inventory."""
        self.visible = not self.visible
        self.selected_item = 0
        
    def handle_input(self, event, player):
        """Handle input events for the inventory."""
        if not self.visible:
            return None
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_item = max(0, self.selected_item - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_item = min(len(player.inventory) - 1, self.selected_item + 1)
            elif event.key == pygame.K_RETURN and player.inventory:
                # Use the selected item
                if 0 <= self.selected_item < len(player.inventory):
                    item = player.inventory[self.selected_item]
                    result = player.use_item(item)
                    return result
            elif event.key == pygame.K_e or event.key == pygame.K_ESCAPE:
                # Close inventory
                self.toggle_visibility()
                
        return None
        
    def draw(self, screen, player):
        """Draw the inventory UI."""
        if not self.visible:
            return
            
        # Draw semi-transparent background
        inventory_surface = pygame.Surface((300, 400))
        inventory_surface.set_alpha(200)
        inventory_surface.fill((0, 0, 0))
        screen.blit(inventory_surface, (self.screen_width // 2 - 150, self.screen_height // 2 - 200))
        
        # Draw title
        title = self.font.render("Inventory", True, (255, 255, 255))
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, self.screen_height // 2 - 180))
        
        # Draw items
        for i, item in enumerate(player.inventory):
            color = (255, 255, 0) if i == self.selected_item else (255, 255, 255)
            item_text = self.font.render(f"{item.name}", True, color)
            screen.blit(item_text, (self.screen_width // 2 - 140, self.screen_height // 2 - 140 + i * 30))
            
            # Show item type
            type_text = self.font.render(f"({item.item_type})", True, color)
            screen.blit(type_text, (self.screen_width // 2 + 50, self.screen_height // 2 - 140 + i * 30))
            
        # Draw instructions
        instructions = self.font.render("UP/DOWN: Navigate, ENTER: Use, E/ESC: Close", True, (200, 200, 200))
        screen.blit(instructions, (self.screen_width // 2 - instructions.get_width() // 2, self.screen_height // 2 + 170))