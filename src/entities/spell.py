"""
Spell class for representing magical spells.
"""

class Spell:
    """A magical spell that can be cast by a character."""
    
    def __init__(self, name, description, mp_cost, effect, target_type="enemy"):
        self.name = name
        self.description = description
        self.mp_cost = mp_cost
        self.effect = effect  # e.g., {"type": "damage", "amount": 15} or {"type": "heal", "amount": 20}
        self.target_type = target_type  # "enemy", "ally", "self"