"""
Character class.
"""

from entities.entity import Entity
from entities.spell import Spell
class Character(Entity):
    """A character in the party."""
    
    def __init__(self, name, hp, mp, attack, defense, portrait=None):
        super().__init__(0, 0, '', name, "A character in the party")
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.mp = mp
        self.max_mp = mp
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        self.attack = attack
        self.defense = defense
        self.equipped_weapon = None
        self.portrait = portrait
        self.spellbook = []
        
    def learn_spell(self, spell):
        """Add a spell to the character's spellbook."""
        self.spellbook.append(spell)

    def cast_spell(self, spell, target):
        """Cast a spell on a target."""
        if self.mp >= spell.mp_cost:
            self.mp -= spell.mp_cost
            # Apply spell effect
            if spell.effect["type"] == "damage":
                target.take_damage(spell.effect["amount"])
            elif spell.effect["type"] == "heal":
                target.heal(spell.effect["amount"])
            return True
        return False

    def take_damage(self, amount):
        """Reduce character HP by amount."""
        self.hp = max(0, self.hp - amount)
        
    def heal(self, amount):
        """Increase character HP by amount."""
        self.hp = min(self.max_hp, self.hp + amount)
        
    def gain_xp(self, amount):
        """Add XP to the character and check for level up."""
        self.xp += amount
        if self.xp >= self.xp_to_next_level:
            self.level_up()
            
    def level_up(self):
        """Increase character level and stats."""
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
        
    def equip_weapon(self, weapon):
        """Equip a weapon."""
        self.equipped_weapon = weapon
        
    def get_attack_power(self):
        """Calculate the character's attack power including equipped weapon."""
        attack = self.attack
        if self.equipped_weapon:
            attack += self.equipped_weapon.attack_bonus
        return attack
        
    def is_alive(self):
        """Check if the character is still alive."""
        return self.hp > 0