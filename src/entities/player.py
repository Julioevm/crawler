"""
Player character class.
"""

from entities.entity import Entity
import math

class Player(Entity):
    """Player character entity."""
    
    def __init__(self, x, y):
        super().__init__(x, y, '@', "Player", "The adventurer exploring the dungeon", light_source={'radius': 8, 'strength': 1.0})
        self.hp = 100
        self.max_hp = 100
        self.mp = 50
        self.max_mp = 50
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        self.attack = 10
        self.defense = 5
        self.inventory = []
        self.equipped_weapon = None
        self.facing = 0  # 0=north, 1=east, 2=south, 3=west
        # Angle in radians corresponding to facing direction
        self.angle = 0.0  # 0 = north, π/2 = east, π = south, 3π/2 = west
        
    def take_damage(self, amount):
        """Reduce player HP by amount."""
        self.hp = max(0, self.hp - amount)
        
    def heal(self, amount):
        """Increase player HP by amount."""
        self.hp = min(self.max_hp, self.hp + amount)
        
    def gain_xp(self, amount):
        """Add XP to the player and check for level up."""
        self.xp += amount
        if self.xp >= self.xp_to_next_level:
            self.level_up()
            
    def level_up(self):
        """Increase player level and stats."""
        self.level += 1
        self.xp -= self.xp_to_next_level
        self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
        
        # Improve stats
        self.max_hp += 10
        self.hp = self.max_hp
        self.max_mp += 5
        self.mp = self.max_mp
        self.attack += 2
        self.defense += 1
        
    def add_to_inventory(self, item):
        """Add an item to the player's inventory."""
        self.inventory.append(item)
        
    def remove_from_inventory(self, item):
        """Remove an item from the player's inventory."""
        if item in self.inventory:
            self.inventory.remove(item)
            
    def equip_weapon(self, weapon):
        """Equip a weapon."""
        self.equipped_weapon = weapon
        
    def get_attack_power(self):
        """Calculate the player's attack power including equipped weapon."""
        attack = self.attack
        if self.equipped_weapon:
            attack += self.equipped_weapon.attack_bonus
        return attack
        
    def use_item(self, item):
        """Use an item from the inventory."""
        if item in self.inventory:
            result = item.use(self)
            self.remove_from_inventory(item)
            return result
        return "You don't have that item."
        
    def turn_left(self):
        """Turn the player 90 degrees counter-clockwise."""
        self.facing = (self.facing - 1) % 4
        # Update angle in radians
        self.angle = self.facing * (math.pi / 2)
        
    def turn_right(self):
        """Turn the player 90 degrees clockwise."""
        self.facing = (self.facing + 1) % 4
        # Update angle in radians
        self.angle = self.facing * (math.pi / 2)
        
    def get_facing_vector(self):
        """Get the movement vector based on the player's facing direction."""
        # North, East, South, West
        vectors = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        return vectors[self.facing]