"""
Combat manager for handling turn-based combat.
"""

import random

class CombatManager:
    """Manages turn-based combat between player and enemies."""
    
    def __init__(self):
        self.in_combat = False
        self.current_enemy = None
        self.combat_log = []
        
    def start_combat(self, party, enemy):
        """Start combat between party and enemy."""
        self.in_combat = True
        self.current_enemy = enemy
        self.combat_log = [f"A {enemy.name} attacks you!"]
        return self.combat_log
        
    def player_attack(self, party, enemy):
        """Process party attack on enemy."""
        # For now, only the first character attacks
        character = party.characters[0]
        # Calculate damage
        damage = max(1, character.get_attack_power() - enemy.defense + random.randint(-2, 2))
        
        # Apply damage
        enemy_dead = enemy.take_damage(damage)
        
        # Add to combat log
        self.combat_log.append(f"{character.name} hit the {enemy.name} for {damage} damage!")
        
        if enemy_dead:
            self.combat_log.append(f"You defeated the {enemy.name}!")
            party.gain_xp(enemy.max_hp)  # Gain XP based on enemy max HP
            self.in_combat = False
            self.current_enemy = None
            return True  # Enemy defeated
            
        return False  # Enemy still alive
        
    def enemy_attack(self, party, enemy):
        """Process enemy attack on party."""
        # Attack a random character
        character = random.choice(party.characters)
        # Calculate damage
        damage = max(1, enemy.attack - character.defense + random.randint(-2, 2))
        
        # Apply damage
        character.take_damage(damage)
        
        # Add to combat log
        self.combat_log.append(f"The {enemy.name} hits {character.name} for {damage} damage!")
        
        if all(c.hp <= 0 for c in party.characters):
            self.combat_log.append("You have been defeated!")
            self.in_combat = False
            self.current_enemy = None
            return True  # Party defeated
            
        return False  # Party still alive
        
    def try_flee(self, party, enemy):
        """Attempt to flee from combat."""
        # 50% chance to flee
        if random.random() < 0.5:
            self.combat_log.append("You successfully flee from combat!")
            self.in_combat = False
            self.current_enemy = None
            return True
        else:
            self.combat_log.append("You failed to flee!")
            return False