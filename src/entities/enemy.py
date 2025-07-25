"""
Basic enemy class.
"""

from entities.entity import Entity
from entities.ai import BasicAI

class Enemy(Entity):
    """Basic enemy entity."""
    
    def __init__(self, x, y, name, hp, attack, defense, sprite=None):
        super().__init__(x, y, 'E', name, f"A {name} lurking in the dungeon", sprite=sprite)
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.defense = defense
        self.ai = BasicAI(self)  # Attach the AI component
        
    def take_damage(self, amount):
        """Reduce enemy HP by amount."""
        self.hp = max(0, self.hp - amount)
        return self.hp <= 0  # Return True if enemy is defeated
        
    def is_alive(self):
        """Check if the enemy is still alive."""
        return self.hp > 0