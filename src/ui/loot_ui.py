"""
Loot UI for displaying and managing items in a container.
"""

import pygame

class LootUI:
    """UI for looting chests and item piles."""

    def __init__(self, screen_width, screen_height, container):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.container = container
        self.font = pygame.font.Font(None, 24)
        self.visible = False
        self.selected_item = 0

    def toggle_visibility(self):
        """Toggle the visibility of the loot UI."""
        self.visible = not self.visible
        self.selected_item = 0

    def handle_input(self, event):
        """Handle input events for the loot UI."""
        if not self.visible:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_item = max(0, self.selected_item - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_item = min(len(self.container.items) - 1, self.selected_item + 1)
            elif event.key == pygame.K_RETURN and self.container.items:
                if 0 <= self.selected_item < len(self.container.items):
                    item = self.container.items[self.selected_item]
                    return {"take": item}
            elif event.key == pygame.K_a:
                return {"take_all": True}
        return None

    def draw(self, screen):
        """Draw the loot UI."""
        if not self.visible:
            return

        # Draw semi-transparent background
        loot_surface = pygame.Surface((300, 400))
        loot_surface.set_alpha(200)
        loot_surface.fill((0, 0, 0))
        screen.blit(loot_surface, (self.screen_width // 2 - 150, self.screen_height // 2 - 200))

        # Draw title
        title = self.font.render(self.container.name, True, (255, 255, 255))
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, self.screen_height // 2 - 180))

        # Draw items
        for i, item in enumerate(self.container.items):
            color = (255, 255, 0) if i == self.selected_item else (255, 255, 255)
            item_text = self.font.render(f"{item.name}", True, color)
            screen.blit(item_text, (self.screen_width // 2 - 140, self.screen_height // 2 - 140 + i * 30))

        # Draw instructions
        instructions = self.font.render("UP/DOWN: Navigate, ENTER: Take, A: Take All", True, (200, 200, 200))
        screen.blit(instructions, (self.screen_width // 2 - instructions.get_width() // 2, self.screen_height // 2 + 170))