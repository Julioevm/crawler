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
        
    def load_texture(self, name, file_path=None):
        """Load a texture from a file or create a colored texture for testing."""
        if file_path and os.path.exists(file_path):
            try:
                texture = pygame.image.load(file_path).convert()
                texture = pygame.transform.scale(texture, (TEXTURE_SIZE, TEXTURE_SIZE))
                self.textures[name] = texture
                return texture
            except pygame.error:
                print(f"Failed to load texture: {file_path}")
        
        # Fallback to creating a simple colored texture
        # In a real game, you would have actual texture files
        texture = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
        if name == "wall_red":
            texture.fill((180, 60, 60))
        elif name == "wall_green":
            texture.fill((60, 180, 60))
        elif name == "wall_blue":
            texture.fill((60, 60, 180))
        elif name == "wall_gray":
            texture.fill((120, 120, 120))
        elif name == "dungeon_wall":
            texture.fill((100, 100, 110))  # Default dungeon wall color
        else:
            texture.fill((200, 200, 200))  # Default light gray
            
        self.textures[name] = texture
        return texture
        
    def load_sprite(self, name, file_path):
        """Load a sprite from a file."""
        print(f"Loading sprite '{name}' from {file_path}", flush=True)
        if os.path.exists(file_path):
            print(f"File exists: {file_path}", flush=True)
            try:
                sprite = pygame.image.load(file_path).convert_alpha()
                self.sprites[name] = sprite
                return sprite
            except pygame.error:
                print(f"Failed to load sprite: {file_path}")
        return None

    def get_texture(self, name):
        """Get a texture by name."""
        return self.textures.get(name)
        
    def get_sprite(self, name):
        """Get a sprite by name."""
        return self.sprites.get(name)
        
    def create_default_textures(self):
        """Create default textures for walls."""
        # Try to load actual texture files first
        self.load_texture("dungeon_wall", os.path.join(self.assets_path, "textures", "dungeon_wall.png"))
        self.load_texture("wall_red", os.path.join(self.assets_path, "textures", "wall_red.png"))
        self.load_texture("wall_green", os.path.join(self.assets_path, "textures", "wall_green.png"))
        self.load_texture("wall_blue", os.path.join(self.assets_path, "textures", "wall_blue.png"))
        self.load_texture("wall_gray", os.path.join(self.assets_path, "textures", "wall_gray.png"))
        
        # Load sprites
        self.load_sprite("goblin", os.path.join(self.assets_path, "sprites", "goblin.png"))
        
        # Also create some simple colored textures as fallbacks
        if "dungeon_wall" not in self.textures:
            self.load_texture("dungeon_wall")
        if "wall_red" not in self.textures:
            self.load_texture("wall_red")
        if "wall_green" not in self.textures:
            self.load_texture("wall_green")
        if "wall_blue" not in self.textures:
            self.load_texture("wall_blue")
        if "wall_gray" not in self.textures:
            self.load_texture("wall_gray")