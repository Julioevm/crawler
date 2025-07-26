"""
EnemyGroup class to hold a group of enemies.
"""

from entities.entity import Entity

class EnemyGroup(Entity):
    """A group of enemies on the map."""
    
    def __init__(self, x, y, enemies):
        sprite_name = enemies[0].sprite if enemies else None
        super().__init__(x, y, 'G', "Enemy Group", "A group of hostile creatures", sprite=sprite_name)
        self.enemies = enemies

    def is_alive(self):
        """Check if there are any living enemies in the group."""
        return any(enemy.is_alive() for enemy in self.enemies)