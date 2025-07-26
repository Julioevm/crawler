import pygame
from .base_state import BaseState
from ui.combat_ui import CombatUI
from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class CombatState(BaseState):
    def __init__(self, game, party, enemies, combat_manager):
        super().__init__()
        self.game = game
        self.party = party
        self.enemies = enemies
        self.combat_manager = combat_manager
        self.combat_ui = CombatUI(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        self.combat_manager.start_combat(self.party, self.enemies)
        self.combat_ui.start_combat(self.party, self.enemies)
        # TODO: Pass combat log to a message system
        self.current_character_index = 0
        self.combat_manager.current_turn_index = self.current_character_index

    def get_event(self, event):
        action_result = self.combat_ui.handle_input(event, self.combat_manager)
        if action_result:
            action = action_result.get("action")
            if action == "attack":
                attacker = self.party.characters[self.current_character_index]
                target = action_result.get("target")
                self.combat_manager.player_attack(attacker, target)
                self.next_turn()
            elif action == "spell":
                attacker = self.party.characters[self.current_character_index]
                spell = action_result.get("spell")
                target = action_result.get("target")
                if attacker.cast_spell(spell, target):
                    self.combat_manager.combat_log.append(f"{attacker.name} casts {spell.name} on {target.name}!")
                else:
                    self.combat_manager.combat_log.append(f"{attacker.name} failed to cast {spell.name}!")
                self.next_turn()
            elif action == "item":
                item = action_result.get("item")
                target = action_result.get("target")
                # We'll need a way to use items on characters
                # For now, let's assume potions heal
                if "potion" in item.name.lower():
                    target.heal(item.heal_amount)
                    self.party.remove_from_inventory(item)
                    self.combat_manager.combat_log.append(f"{target.name} uses a {item.name} and heals for {item.heal_amount} HP.")
                self.next_turn()
            elif action == "guard":
                # Implement guard logic
                self.next_turn()
            elif action == "flee":
                if self.combat_manager.try_flee():
                    self.done = True
                else:
                    self.enemy_turn()

    def next_turn(self):
        self.current_character_index += 1
        if self.current_character_index >= len(self.party.characters):
            self.enemy_turn()
        else:
            self.combat_manager.current_turn_index = self.current_character_index

        combat_result = self.combat_manager.check_combat_end()
        if combat_result:
            self.end_combat(combat_result)

    def enemy_turn(self):
        for enemy in self.combat_manager.enemies:
            if enemy.is_alive():
                self.combat_manager.enemy_attack(enemy, self.party)
        
        self.current_character_index = 0
        self.combat_manager.current_turn_index = self.current_character_index
        combat_result = self.combat_manager.check_combat_end()
        if combat_result:
            self.end_combat(combat_result)

    def end_combat(self, result):
        if result == "victory":
            # Keep the original list of enemies to remove them from the map
            for enemy in self.enemies:
                if enemy in self.game.playing_state.game_map.entities:
                    self.game.playing_state.game_map.remove_entity(enemy)
        elif result == "defeat":
            self.quit = True
        self.done = True

    def draw(self, screen, clock):
        # Draw the underlying playing state
        self.game.playing_state.draw(screen, clock)
        # Draw the combat UI over it
        self.combat_ui.draw(screen, self.combat_manager)