from .base_state import BaseState

class CombatState(BaseState):
    def __init__(self, game, party, enemies, combat_manager):
        super().__init__()
        self.game = game
        self.party = party
        self.enemies = enemies
        self.combat_manager = combat_manager
        self.combat_ui = self.game.game_gui.combat_ui
        
        self.combat_manager.start_combat(self.party, self.enemies)
        self.combat_ui.start_combat(self.party, self.enemies)
        self.combat_ui.build()
        self.combat_ui.show()
        
        self.current_character_index = 0
        self.combat_manager.current_turn_index = self.current_character_index

    def get_event(self, event):
        action_result = self.combat_ui.handle_event(event)
        if action_result:
            action = action_result.get("action")
            if action == "attack":
                attacker = self.party.characters[self.current_character_index]
                target = action_result.get("target")
                try:
                    target_index = self.enemies.index(target)
                except ValueError:
                    self.next_turn()
                    return

                target_dead, damage = self.combat_manager.player_attack(attacker, target)
                
                if damage > 0:
                    self.combat_ui.show_damage(target_index, damage)

                if target_dead:
                    self.combat_ui.build_enemy_display()

                self.next_turn()
            elif action == "spell":
                attacker = self.party.characters[self.current_character_index]
                spell = action_result.get("spell")
                target = action_result.get("target")
                if attacker.cast_spell(spell, target):
                    self.game.game_gui.add_message(f"{attacker.name} casts {spell.name} on {target.name}!")
                else:
                    self.game.game_gui.add_message(f"{attacker.name} failed to cast {spell.name}!")
                self.next_turn()
            elif action == "item":
                item = action_result.get("item")
                target = action_result.get("target")
                # We'll need a way to use items on characters
                # For now, let's assume potions heal
                if "potion" in item.name.lower():
                    target.heal(item.heal_amount)
                    self.party.remove_from_inventory(item)
                    self.game.game_gui.add_message(f"{target.name} uses a {item.name} and heals for {item.heal_amount} HP.")
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
                target, _, damage = self.combat_manager.enemy_attack(enemy, self.party)
                if damage > 0 and target:
                    try:
                        target_index = self.party.characters.index(target)
                        self.game.game_gui.show_damage_on_party_member(target_index, damage)
                    except ValueError:
                        # Target not in party, should not happen
                        pass
        
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
        self.combat_ui.end_combat()

    def draw(self, screen, clock):
        # Draw the underlying playing state
        self.game.playing_state.draw(screen, clock)
        # The main game loop now handles drawing the GUI,
        # so we don't need to call combat_ui.draw() here.