"""
Basic UI system for displaying game information.
"""

import pygame

class UI:
    """Basic UI system for the game."""
    
    def __init__(self, screen_width, screen_height, show_fps=False):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.show_fps = show_fps
        
    def draw_player_stats(self, screen, player):
        """Draw player stats on the screen."""
        # Create a semi-transparent background for the stats
        stats_surface = pygame.Surface((200, 130))
        stats_surface.set_alpha(128)
        stats_surface.fill((0, 0, 0))
        screen.blit(stats_surface, (10, 10))
        
        # Draw player stats
        hp_text = self.font.render(f"HP: {player.hp}/{player.max_hp}", True, (255, 255, 255))
        mp_text = self.font.render(f"MP: {player.mp}/{player.max_mp}", True, (255, 255, 255))
        level_text = self.font.render(f"Level: {player.level}", True, (255, 255, 255))
        
        # Draw compass direction
        directions = ["N", "E", "S", "W"]
        direction_text = self.font.render(f"Facing: {directions[player.facing]}", True, (255, 255, 255))
        
        screen.blit(hp_text, (20, 20))
        screen.blit(mp_text, (20, 50))
        screen.blit(level_text, (20, 80))
        screen.blit(direction_text, (20, 110))
        
    def draw_messages(self, screen, messages):
        """Draw game messages on the screen."""
        # Draw messages in the bottom-left corner
        y_offset = self.screen_height - 40
        for message in reversed(messages[-5:]):  # Show last 5 messages
            text = self.small_font.render(message, True, (255, 255, 255))
            screen.blit(text, (10, y_offset))
            y_offset -= 30

    def draw_fps(self, screen, fps):
        """Draw the FPS counter on the screen."""
        if self.show_fps:
            fps_text = self.font.render(f"FPS: {fps:.2f}", True, (255, 255, 255))
            screen.blit(fps_text, (self.screen_width - 150, 10))