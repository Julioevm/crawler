"""
Raycasting engine for the first-person view in the dungeon crawler.
Based on the technique used in Wolfenstein 3D.
"""

import math
import pygame

class Raycaster:
    def __init__(self, screen_width, screen_height, map_data, texture_manager=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_data = map_data
        self.map_width = len(map_data[0])
        self.map_height = len(map_data)
        self.texture_manager = texture_manager
        
        # Player properties (center of the grid cell)
        self.player_x = 1.5
        self.player_y = 1.5
        self.player_angle = 0
        
        # Rendering properties
        self.fov = math.pi / 3  # 60 degrees field of view
        self.wall_height = 64
        self.wall_colors = {
            1: (100, 100, 110),  # Dungeon wall color
        }
        
        # Texture size
        self.tex_width = 64
        self.tex_height = 64
        
        # Create default textures if no texture manager provided
        if not self.texture_manager:
            from engine.texture_manager import TextureManager
            self.texture_manager = TextureManager()
            self.texture_manager.create_default_textures()
    
    def set_player_position(self, x, y):
        """Set the player's position"""
        self.player_x = x + 0.5  # Center of the cell
        self.player_y = y + 0.5  # Center of the cell
    
    def set_player_angle(self, angle):
        """Set the player's viewing angle"""
        self.player_angle = angle
    
    def cast_rays(self, screen):
        """Cast rays and render the 3D view"""
        # Cast one ray for each column of the screen
        for x in range(self.screen_width):
            # Calculate the ray angle
            ray_angle = self.player_angle - self.fov / 2 + (x / self.screen_width) * self.fov
            
            # Normalize the angle
            ray_angle = ray_angle % (2 * math.pi)
            
            # Cast the ray
            distance, wall_type, hit_x, hit_y = self.cast_single_ray(ray_angle)
            
            # Correct for fisheye effect
            distance *= math.cos(ray_angle - self.player_angle)
            
            # Calculate wall height
            wall_height = (self.wall_height / distance) if distance > 0 else self.screen_height
            
            # Use dungeon wall texture for all walls
            texture = self.texture_manager.get_texture("dungeon_wall")
            
            # Draw textured wall slice if texture is available
            if wall_type > 0 and texture:
                # Calculate wall position
                wall_top = (self.screen_height - wall_height) // 2
                wall_bottom = wall_top + wall_height
                
                # Calculate texture coordinate
                # Get the exact position where the ray hit the wall
                wall_x = hit_x if hit_x is not None else 0
                wall_y = hit_y if hit_y is not None else 0
                
                # Calculate texture coordinate (0-1) across the wall
                tex_coord = wall_x - math.floor(wall_x) if (wall_x - math.floor(wall_x)) != 0 else 1
                if hit_x is None:  # If hit_y was used instead
                    tex_coord = wall_y - math.floor(wall_y) if (wall_y - math.floor(wall_y)) != 0 else 1
                    
                # Map to texture pixel coordinate
                tex_x = int(tex_coord * (self.tex_width - 1))
                
                # Ensure tex_x is within bounds
                tex_x = max(0, min(self.tex_width - 1, tex_x))
                
                # Extract a single column from the texture
                tex_column = texture.subsurface((tex_x, 0, 1, self.tex_height))
                
                # Scale the texture column to match the wall height
                scaled_column = pygame.transform.scale(tex_column, (1, int(wall_height)))
                screen.blit(scaled_column, (x, wall_top))
            elif wall_type > 0:
                # Fallback to solid color if texture not available
                color = self.wall_colors.get(wall_type, (100, 100, 110))
                wall_top = (self.screen_height - wall_height) // 2
                wall_bottom = wall_top + wall_height
                pygame.draw.line(screen, color, (x, wall_top), (x, wall_bottom))
            else:
                # Draw empty space (don't draw anything)
                pass
        
        # Draw a simple floor
        pygame.draw.rect(screen, (50, 50, 50), (0, self.screen_height // 2, self.screen_width, self.screen_height // 2))
    
    def cast_single_ray(self, ray_angle):
        """Cast a single ray and return the distance to the first wall hit, the wall type, and hit coordinates"""
        # Ray direction
        ray_dir_x = math.cos(ray_angle)
        ray_dir_y = math.sin(ray_angle)
        
        # Player's map position
        map_x = int(self.player_x)
        map_y = int(self.player_y)
        
        # Length of ray from current position to next x or y-side
        delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else float('inf')
        delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else float('inf')
        
        # Direction to step in x or y direction (either +1 or -1)
        step_x = 1 if ray_dir_x >= 0 else -1
        step_y = 1 if ray_dir_y >= 0 else -1
        
        # Length of ray from one side to next in map
        if ray_dir_x < 0:
            side_dist_x = (self.player_x - map_x) * delta_dist_x
        else:
            side_dist_x = (map_x + 1.0 - self.player_x) * delta_dist_x
            
        if ray_dir_y < 0:
            side_dist_y = (self.player_y - map_y) * delta_dist_y
        else:
            side_dist_y = (map_y + 1.0 - self.player_y) * delta_dist_y
        
        # Perform DDA (Digital Differential Analysis)
        hit = False
        side = 0  # 0 for x-side, 1 for y-side
        
        while not hit:
            # Jump to next map square, either in x-direction, or in y-direction
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
                
            # Check if ray has hit a wall
            if 0 <= map_x < self.map_width and 0 <= map_y < self.map_height:
                if self.map_data[map_y][map_x] > 0:
                    hit = True
            else:
                # Ray went outside the map
                break
        
        # Calculate distance projected on camera direction
        if side == 0:
            perp_wall_dist = (map_x - self.player_x + (1 - step_x) / 2) / ray_dir_x
            # Calculate exact hit position
            hit_y = self.player_y + perp_wall_dist * ray_dir_y
            hit_x = map_x if ray_dir_x > 0 else map_x + 1
        else:
            perp_wall_dist = (map_y - self.player_y + (1 - step_y) / 2) / ray_dir_y
            # Calculate exact hit position
            hit_x = self.player_x + perp_wall_dist * ray_dir_x
            hit_y = map_y if ray_dir_y > 0 else map_y + 1
            
        return perp_wall_dist, self.map_data[map_y][map_x] if hit else 0, hit_x, hit_y