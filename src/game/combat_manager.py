import random

class CombatManager:
    """Manages turn-based combat between the player's party and enemy groups."""

    def __init__(self, game_gui):
        self.game_gui = game_gui
        self.in_combat = False
        self.party = None
        self.enemies = []
        self.combatants = []  # List of all combatants, sorted by initiative
        self.current_turn_index = 0

    def start_combat(self, party, enemies):
        """Start combat between the party and a group of enemies."""
        self.in_combat = True
        self.party = party
        self.enemies = enemies
        self.game_gui.add_message(f"A group of {len(enemies)} enemies attacks you!")
        
        # Combine party members and enemies into a single list of combatants
        self.combatants = self.party.characters + self.enemies
        # For now, let's not worry about initiative and just alternate turns
        # A more sophisticated system will be added later.
        self.current_turn_index = 0

    def end_combat(self):
        """End the current combat."""
        self.in_combat = False
        self.party = None
        self.enemies = []
        self.combatants = []
        self.current_turn_index = 0

    def player_attack(self, attacker, target):
        """Process a player character's attack on an enemy."""
        damage = max(1, attacker.get_attack_power() - target.defense + random.randint(-2, 2))
        target_dead = target.take_damage(damage)
        
        self.game_gui.add_message(f"{attacker.name} hits {target.name} for {damage} damage!")
        
        if target_dead:
            self.game_gui.add_message(f"You defeated {target.name}!")
            self.party.gain_xp(target.max_hp)
            self.combatants.remove(target)
            self.enemies.remove(target)
        
        return target_dead, damage

    def enemy_attack(self, attacker, party):
        """Process an enemy's attack on a random party member."""
        # Check morale
        if attacker.morale < 30 and random.random() < 0.5:
            self.game_gui.add_message(f"{attacker.name} has fled the battle!")
            self.combatants.remove(attacker)
            self.enemies.remove(attacker)
            return None, None, 0

        target = random.choice(party.characters)
        damage = max(1, attacker.attack - target.defense + random.randint(-2, 2))
        target_dead = target.take_damage(damage)
        
        self.game_gui.add_message(f"{attacker.name} hits {target.name} for {damage} damage!")
        
        if target.hp <= 0:
            self.game_gui.add_message(f"{target.name} has been defeated!")
            # Lower morale of other enemies
            for enemy in self.enemies:
                if enemy is not attacker:
                    enemy.morale -= 10
        
        return target, target_dead, damage

    def check_combat_end(self):
        """Check if combat should end."""
        if not any(enemy.is_alive() for enemy in self.enemies):
            self.game_gui.add_message("You have won the battle!")
            self.end_combat()
            return "victory"
            
        if not any(character.hp > 0 for character in self.party.characters):
            self.game_gui.add_message("You have been defeated!")
            self.end_combat()
            return "defeat"
            
        return None

    def try_flee(self):
        """Attempt to flee from combat."""
        if random.random() < 0.5:  # 50% chance to flee
            self.game_gui.add_message("You successfully flee from combat!")
            self.end_combat()
            return True
        else:
            self.game_gui.add_message("You failed to flee!")
            return False