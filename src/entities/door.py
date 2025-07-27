from .entity import Entity

class Door(Entity):
    """
    Represents a door that can be opened and closed.
    """
    def __init__(self, x, y, is_open=False):
        super().__init__(x, y, "D", "Door")
        self.is_open = is_open
        self.blocks_movement = not self.is_open
        self.texture_open = "dungeon_door_open"
        self.texture_closed = "dungeon_door_closed"

    @property
    def texture(self):
        """Return the appropriate texture based on the door's state."""
        return self.texture_open if self.is_open else self.texture_closed

    def open(self, game_map):
        """Open the door and update the map."""
        if not self.is_open:
            self.is_open = True
            self.blocks_movement = False
            game_map.tiles[int(self.y)][int(self.x)] = 3  # Set tile to open door
            # We might want to add a sound effect here later

    def close(self, game_map):
        """Close the door and update the map."""
        if self.is_open:
            self.is_open = False
            self.blocks_movement = True
            game_map.tiles[int(self.y)][int(self.x)] = 2  # Set tile to door
            # We might want to add a sound effect here later

    def interact(self, game_map):
        """Interact with the door (open/close)."""
        if self.is_open:
            self.close(game_map)
        else:
            self.open(game_map)