"""
Raycasting engine for the first-person view in the dungeon crawler.
Based on the technique used in Wolfenstein 3D.
"""

import math
import pygame

class Raycaster:
    def __init__(self, screen_width, screen_height, map_data):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_data = map_data
        self.map_width = len(map_data[0])
        self.map_height = len(map_data)
        
        # Player properties (center of the grid cell)
        self.player_x = 1.5
        self.player_y = 1.5
        self.player_angle = 0
        
        # Rendering properties
        self.fov = math.pi / 3  # 60 degrees field of view
        self.wall_height = 64
        self.wall_colors = {
            1: (200, 0, 0),    # Red walls
            2: (0, 200, 0),    # Green walls
            3: (0, 0, 200),    # Blue walls
        }
    
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
            distance, wall_type = self.cast_single_ray(ray_angle)
            
            # Correct for fisheye effect
            distance *= math.cos(ray_angle - self.player_angle)
            
            # Calculate wall height
            wall_height = (self.wall_height / distance) if distance > 0 else self.screen_height
            
            # Calculate wall color based on type
            color = self.wall_colors.get(wall_type, (100, 100, 100))
            
            # Draw the wall slice
            wall_top = (self.screen_height - wall_height) // 2
            wall_bottom = wall_top + wall_height
            
            pygame.draw.line(screen, color, (x, wall_top), (x, wall_bottom))
        
        # Draw a simple floor
        pygame.draw.rect(screen, (50, 50, 50), (0, self.screen_height // 2, self.screen_width, self.screen_height // 2))
    
    def cast_single_ray(self, ray_angle):
        """Cast a single ray and return the distance to the first wall hit and the wall type"""
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
        else:
            perp_wall_dist = (map_y - self.player_y + (1 - step_y) / 2) / ray_dir_y
            
        return perp_wall_dist, self.map_data[map_y][map_x] if hit else 0