"""
Texture manager for loading and managing textures.
"""

import pygame
import os
from config.constants import TEXTURE_SIZE

class TextureManager:
    """Manages loading and storing textures for the game."""
    
    def __init__(self, assets_path="assets"):
        self.assets_path = assets_path
        self.textures = {}
        self.sprites = {}
        self.texture_arrays = {}
        self.portraits = {}

    def load_portrait(self, name, file_path):
        """Load a portrait from a file."""
        if not os.path.exists(file_path):
            print(f"Portrait file not found: {file_path}")
            return None
        try:
            portrait = pygame.image.load(file_path).convert_alpha()
            self.portraits[name] = portrait
            return portrait
        except pygame.error as e:
            print(f"Failed to load portrait: {file_path} - {e}")
            return None

    def load_texture(self, name, file_path):
        """Load a texture from a file."""
        if not os.path.exists(file_path):
            print(f"Texture file not found: {file_path}")
            return None
            
        try:
            texture = pygame.image.load(file_path).convert_alpha()
            texture = pygame.transform.scale(texture, (TEXTURE_SIZE, TEXTURE_SIZE))
            self.textures[name] = texture
            self.texture_arrays[name] = pygame.surfarray.array3d(texture)
            return texture
        except pygame.error as e:
            print(f"Failed to load texture: {file_path} - {e}")
            return None

    def load_sprite(self, name, file_path):
        """Load a sprite from a file."""
        if not os.path.exists(file_path):
            print(f"Sprite file not found: {file_path}")
            return None
        try:
            sprite = pygame.image.load(file_path).convert_alpha()
            self.sprites[name] = sprite
            return sprite
        except pygame.error as e:
            print(f"Failed to load sprite: {file_path} - {e}")
            return None

    def get_texture(self, name):
        """Get a texture by name."""
        return self.textures.get(name)

    def get_texture_array(self, name):
        """Get a texture as a numpy array by name."""
        return self.texture_arrays.get(name)

    def get_sprite(self, name):
        """Get a sprite by name."""
        return self.sprites.get(name)

    def get_portrait(self, name):
        """Get a portrait by name."""
        return self.portraits.get(name)
        
    def create_default_textures(self):
        """Create default textures for walls."""
        # Load textures
        self.load_texture("dungeon_wall", os.path.join(self.assets_path, "textures", "dungeon_wall.png"))
        self.load_texture("dungeon_floor", os.path.join(self.assets_path, "textures", "dungeon_floor.png"))
        self.load_texture("dungeon_ceil", os.path.join(self.assets_path, "textures", "dungeon_ceil.png"))
        self.load_texture("dungeon_door_closed", os.path.join(self.assets_path, "textures", "dungeon_door_closed.png"))
        self.load_texture("dungeon_door_open", os.path.join(self.assets_path, "textures", "dungeon_door_open.png"))
        
        # Load sprites
        self.load_sprite("goblin", os.path.join(self.assets_path, "sprites", "goblin.png"))
        self.load_sprite("slime", os.path.join(self.assets_path, "sprites", "slime.png"))
        self.load_sprite("chest", os.path.join(self.assets_path, "sprites", "chest.png"))
        self.load_sprite("item_pile", os.path.join(self.assets_path, "sprites", "item_pile.png"))