"""
Texture manager for loading and managing textures.
"""

import pygame
import os

class TextureManager:
    """Manages loading and storing textures for the game."""
    
    def __init__(self, assets_path="assets"):
        self.assets_path = assets_path
        self.textures = {}
        
    def load_texture(self, name, file_path=None):
        """Load a texture from a file or create a colored texture for testing."""
        if file_path and os.path.exists(file_path):
            try:
                texture = pygame.image.load(file_path).convert()
                self.textures[name] = texture
                return texture
            except pygame.error:
                print(f"Failed to load texture: {file_path}")
        
        # Fallback to creating a simple colored texture
        # In a real game, you would have actual texture files
        texture = pygame.Surface((64, 64))
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
        
    def get_texture(self, name):
        """Get a texture by name."""
        return self.textures.get(name)
        
    def create_default_textures(self):
        """Create default textures for walls."""
        # Try to load actual texture files first
        self.load_texture("dungeon_wall", os.path.join(self.assets_path, "textures", "dungeon_wall.png"))
        self.load_texture("wall_red", os.path.join(self.assets_path, "textures", "wall_red.png"))
        self.load_texture("wall_green", os.path.join(self.assets_path, "textures", "wall_green.png"))
        self.load_texture("wall_blue", os.path.join(self.assets_path, "textures", "wall_blue.png"))
        self.load_texture("wall_gray", os.path.join(self.assets_path, "textures", "wall_gray.png"))
        
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