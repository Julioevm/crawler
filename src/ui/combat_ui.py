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
        self.selected_target = 0
        self.selected_spell = 0
        self.selected_item = 0
        self.actions = ["Attack", "Spell", "Item", "Guard", "Flee"]
        self.spell_menu_active = False
        self.item_menu_active = False

    def start_combat(self, party, enemies):
        """Start combat display."""
        self.visible = True
        self.selected_action = 0
        self.selected_target = 0
        self.party = party
        self.enemies = enemies

    def end_combat(self):
        """End combat display."""
        self.visible = False
        self.party = None
        self.enemies = []

    def handle_input(self, event, combat_manager):
        """Handle input events for combat."""
        if not self.visible or not combat_manager.in_combat:
            return None

        if event.type == pygame.KEYDOWN:
            if self.spell_menu_active:
                if event.key == pygame.K_UP:
                    self.selected_spell = max(0, self.selected_spell - 1)
                elif event.key == pygame.K_DOWN:
                    active_char = self.party.characters[combat_manager.current_turn_index]
                    self.selected_spell = min(len(active_char.spellbook) - 1, self.selected_spell + 1)
                elif event.key == pygame.K_RETURN:
                    active_char = self.party.characters[combat_manager.current_turn_index]
                    spell = active_char.spellbook[self.selected_spell]
                    target = self.enemies[self.selected_target] # Simplification
                    self.spell_menu_active = False
                    return {"action": "spell", "spell": spell, "target": target}
                elif event.key == pygame.K_ESCAPE:
                    self.spell_menu_active = False
            elif self.item_menu_active:
                if event.key == pygame.K_UP:
                    self.selected_item = max(0, self.selected_item - 1)
                elif event.key == pygame.K_DOWN:
                    self.selected_item = min(len(self.party.inventory) - 1, self.selected_item + 1)
                elif event.key == pygame.K_RETURN:
                    item = self.party.inventory[self.selected_item]
                    target = self.party.characters[0] # Simplification
                    self.item_menu_active = False
                    return {"action": "item", "item": item, "target": target}
                elif event.key == pygame.K_ESCAPE:
                    self.item_menu_active = False
            else:
                if event.key == pygame.K_UP:
                    self.selected_action = max(0, self.selected_action - 1)
                elif event.key == pygame.K_DOWN:
                    self.selected_action = min(len(self.actions) - 1, self.selected_action + 1)
                elif event.key == pygame.K_LEFT:
                    self.selected_target = max(0, self.selected_target - 1)
                elif event.key == pygame.K_RIGHT:
                    self.selected_target = min(len(self.enemies) - 1, self.selected_target + 1)
                elif event.key == pygame.K_RETURN:
                    action = self.actions[self.selected_action]
                    if action == "Attack":
                        if self.enemies:
                            target = self.enemies[self.selected_target]
                            return {"action": "attack", "target": target}
                    elif action == "Spell":
                        self.spell_menu_active = True
                    elif action == "Item":
                        self.item_menu_active = True
                    elif action == "Flee":
                        return {"action": "flee"}
                    elif action == "Guard":
                        return {"action": "guard"}

        return None

    def draw(self, screen, combat_manager):
        """Draw the combat UI."""
        if not self.visible or not combat_manager.in_combat:
            return

        # Draw semi-transparent background
        combat_surface = pygame.Surface((self.screen_width, self.screen_height))
        combat_surface.set_alpha(220)
        combat_surface.fill((0, 0, 0))
        screen.blit(combat_surface, (0, 0))

        self.draw_enemies(screen)
        self.draw_party(screen, combat_manager)
        self.draw_actions_menu(screen, combat_manager)
        self.draw_combat_log(screen, combat_manager)

    def draw_enemies(self, screen):
        """Draw the enemy group."""
        x_offset = 0
        for i, enemy in enumerate(self.enemies):
            color = (255, 255, 0) if i == self.selected_target else (255, 100, 100)
            enemy_name = self.font.render(enemy.name, True, color)
            screen.blit(enemy_name, (100 + x_offset, 100))
            
            # Draw HP bar
            hp_bar_width = 100
            hp_percentage = enemy.hp / enemy.max_hp
            pygame.draw.rect(screen, (100, 0, 0), (100 + x_offset, 140, hp_bar_width, 20))
            pygame.draw.rect(screen, (0, 255, 0), (100 + x_offset, 140, hp_bar_width * hp_percentage, 20))
            
            enemy_hp_text = self.small_font.render(f"{enemy.hp}/{enemy.max_hp}", True, (255, 255, 255))
            screen.blit(enemy_hp_text, (100 + x_offset + hp_bar_width + 5, 140))
            x_offset += 150

    def draw_party(self, screen, combat_manager):
        """Draw the player's party."""
        y_offset = 0
        for i, character in enumerate(self.party.characters):
            color = (100, 255, 100)
            if i == combat_manager.current_turn_index:
                color = (255, 255, 0) # Highlight active character

            character_name = self.font.render(character.name, True, color)
            screen.blit(character_name, (50, self.screen_height - 200 + y_offset))

            # HP and MP bars
            hp_bar_width = 100
            hp_percentage = character.hp / character.max_hp
            pygame.draw.rect(screen, (100, 0, 0), (50, self.screen_height - 170 + y_offset, hp_bar_width, 15))
            pygame.draw.rect(screen, (0, 255, 0), (50, self.screen_height - 170 + y_offset, hp_bar_width * hp_percentage, 15))
            hp_text = self.small_font.render(f"HP: {character.hp}/{character.max_hp}", True, (255, 255, 255))
            screen.blit(hp_text, (160, self.screen_height - 170 + y_offset))

            mp_bar_width = 100
            mp_percentage = character.mp / character.max_mp
            pygame.draw.rect(screen, (0, 0, 100), (50, self.screen_height - 150 + y_offset, mp_bar_width, 15))
            pygame.draw.rect(screen, (0, 100, 255), (50, self.screen_height - 150 + y_offset, mp_bar_width * mp_percentage, 15))
            mp_text = self.small_font.render(f"MP: {character.mp}/{character.max_mp}", True, (255, 255, 255))
            screen.blit(mp_text, (160, self.screen_height - 150 + y_offset))
            
            y_offset += 60

    def draw_actions_menu(self, screen, combat_manager):
        """Draw the combat actions menu."""
        if self.spell_menu_active:
            self.draw_spell_menu(screen, combat_manager)
        elif self.item_menu_active:
            self.draw_item_menu(screen)
        else:
            y_offset = 0
            for i, action in enumerate(self.actions):
                color = (255, 255, 0) if i == self.selected_action else (255, 255, 255)
                action_text = self.font.render(action, True, color)
                screen.blit(action_text, (self.screen_width - 200, self.screen_height - 200 + y_offset))
                y_offset += 40

    def draw_spell_menu(self, screen, combat_manager):
        """Draw the spell selection menu."""
        y_offset = 0
        active_char = self.party.characters[combat_manager.current_turn_index]
        for i, spell in enumerate(active_char.spellbook):
            color = (255, 255, 0) if i == self.selected_spell else (255, 255, 255)
            spell_text = self.font.render(f"{spell.name} ({spell.mp_cost} MP)", True, color)
            screen.blit(spell_text, (self.screen_width - 250, self.screen_height - 200 + y_offset))
            y_offset += 40

    def draw_item_menu(self, screen):
        """Draw the item selection menu."""
        y_offset = 0
        for i, item in enumerate(self.party.inventory):
            color = (255, 255, 0) if i == self.selected_item else (255, 255, 255)
            item_text = self.font.render(item.name, True, color)
            screen.blit(item_text, (self.screen_width - 200, self.screen_height - 200 + y_offset))
            y_offset += 40

    def draw_combat_log(self, screen, combat_manager):
        """Draw the combat log."""
        log_y = self.screen_height - 400
        for message in combat_manager.combat_log[-5:]:  # Show last 5 messages
            log_text = self.small_font.render(message, True, (255, 255, 200))
            screen.blit(log_text, (50, log_y))
            log_y += 25