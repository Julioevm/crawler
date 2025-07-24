"""
Combat UI for displaying and managing combat interactions.
"""

import pygame

class CombatUI:
    """UI for displaying and managing combat."""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.visible = False
        self.selected_action = 0
        self.actions = ["Attack", "Flee"]  # Simplified for now
        
    def start_combat(self, player, enemy):
        """Start combat display."""
        self.visible = True
        self.selected_action = 0
        self.player = player
        self.enemy = enemy
        
    def end_combat(self):
        """End combat display."""
        self.visible = False
        self.player = None
        self.enemy = None
        
    def handle_input(self, event, combat_manager):
        """Handle input events for combat."""
        if not self.visible or not combat_manager.in_combat:
            return None
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_action = max(0, self.selected_action - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_action = min(len(self.actions) - 1, self.selected_action + 1)
            elif event.key == pygame.K_RETURN:
                # Execute selected action
                action = self.actions[self.selected_action]
                if action == "Attack":
                    enemy_defeated = combat_manager.player_attack(self.player, self.enemy)
                    if not enemy_defeated and combat_manager.in_combat:
                        # Enemy gets a turn if still alive
                        player_defeated = combat_manager.enemy_attack(self.player, self.enemy)
                        if player_defeated:
                            return "defeat"
                    else:
                        # Enemy was defeated
                        self.end_combat()
                        return "victory"
                elif action == "Flee":
                    fled = combat_manager.try_flee(self.player, self.enemy)
                    if fled:
                        self.end_combat()
                        return "fled"
                    else:
                        # Enemy gets a turn if flee failed
                        player_defeated = combat_manager.enemy_attack(self.player, self.enemy)
                        if player_defeated:
                            return "defeat"
                            
        return None
        
    def draw(self, screen, combat_manager):
        """Draw the combat UI."""
        if not self.visible or not combat_manager.in_combat:
            return
            
        # Draw semi-transparent background
        combat_surface = pygame.Surface((500, 400))
        combat_surface.set_alpha(200)
        combat_surface.fill((50, 0, 0))  # Dark red for combat
        screen.blit(combat_surface, (self.screen_width // 2 - 250, self.screen_height // 2 - 200))
        
        # Draw combat title
        title = self.font.render("COMBAT", True, (255, 255, 255))
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, self.screen_height // 2 - 180))
        
        # Draw enemy info
        enemy_text = self.font.render(f"{self.enemy.name}", True, (255, 100, 100))
        screen.blit(enemy_text, (self.screen_width // 2 - enemy_text.get_width() // 2, self.screen_height // 2 - 140))
        
        enemy_hp = self.small_font.render(f"HP: {self.enemy.hp}/{self.enemy.max_hp}", True, (255, 255, 255))
        screen.blit(enemy_hp, (self.screen_width // 2 - enemy_hp.get_width() // 2, self.screen_height // 2 - 110))
        
        # Draw player info
        player_text = self.font.render(f"{self.player.name}", True, (100, 255, 100))
        screen.blit(player_text, (self.screen_width // 2 - player_text.get_width() // 2, self.screen_height // 2 - 50))
        
        player_hp = self.small_font.render(f"HP: {self.player.hp}/{self.player.max_hp}", True, (255, 255, 255))
        screen.blit(player_hp, (self.screen_width // 2 - player_hp.get_width() // 2, self.screen_height // 2 - 20))
        
        # Draw actions
        for i, action in enumerate(self.actions):
            color = (255, 255, 0) if i == self.selected_action else (255, 255, 255)
            action_text = self.font.render(action, True, color)
            screen.blit(action_text, (self.screen_width // 2 - action_text.get_width() // 2, self.screen_height // 2 + 30 + i * 40))
            
        # Draw combat log
        log_y = self.screen_height // 2 + 130
        for message in combat_manager.combat_log[-3:]:  # Show last 3 messages
            log_text = self.small_font.render(message, True, (255, 255, 200))
            screen.blit(log_text, (self.screen_width // 2 - 240, log_y))
            log_y += 25