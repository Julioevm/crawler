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
        
    def start_combat(self, player, enemy):
        """Start combat between player and enemy."""
        self.in_combat = True
        self.current_enemy = enemy
        self.combat_log = [f"A {enemy.name} attacks you!"]
        return self.combat_log
        
    def player_attack(self, player, enemy):
        """Process player attack on enemy."""
        # Calculate damage
        damage = max(1, player.get_attack_power() - enemy.defense + random.randint(-2, 2))
        
        # Apply damage
        enemy_dead = enemy.take_damage(damage)
        
        # Add to combat log
        self.combat_log.append(f"You hit the {enemy.name} for {damage} damage!")
        
        if enemy_dead:
            self.combat_log.append(f"You defeated the {enemy.name}!")
            player.gain_xp(enemy.max_hp)  # Gain XP based on enemy max HP
            self.in_combat = False
            self.current_enemy = None
            return True  # Enemy defeated
            
        return False  # Enemy still alive
        
    def enemy_attack(self, player, enemy):
        """Process enemy attack on player."""
        # Calculate damage
        damage = max(1, enemy.attack - player.defense + random.randint(-2, 2))
        
        # Apply damage
        player.take_damage(damage)
        
        # Add to combat log
        self.combat_log.append(f"The {enemy.name} hits you for {damage} damage!")
        
        if player.hp <= 0:
            self.combat_log.append("You have been defeated!")
            self.in_combat = False
            self.current_enemy = None
            return True  # Player defeated
            
        return False  # Player still alive
        
    def try_flee(self, player, enemy):
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