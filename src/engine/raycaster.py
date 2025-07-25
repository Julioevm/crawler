"""
Raycasting engine for the first-person view in the dungeon crawler.
Based on the technique used in Wolfenstein 3D.
"""

import math
import pygame
from config.constants import TEXTURE_SIZE

class Raycaster:
    def __init__(self, screen_width, screen_height, game_map, texture_manager=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game_map = game_map
        self.map_data = game_map.tiles
        self.map_width = len(self.map_data[0])
        self.map_height = len(self.map_data)
        self.texture_manager = texture_manager
        
        # Player properties (center of the grid cell)
        self.player_x = 1.5
        self.player_y = 1.5
        self.player_angle = 0
        
        # Rendering properties
        self.fov = math.pi * 5 / 12  # 75 degrees field of view
        # Distance to the projection plane. This is key for a correct 3D projection.
        # It is calculated based on the screen width and the field of view.
        # This replaces the arbitrary `wall_height` scaling factor.
        self.projection_plane_dist = (self.screen_width / 2) / math.tan(self.fov / 2)
        self.wall_colors = {
            1: (100, 100, 110),  # Dungeon wall color
        }
        
        # Texture size
        self.tex_width = TEXTURE_SIZE
        self.tex_height = TEXTURE_SIZE
        
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
        # Render floor and ceiling first
        self.render_floor_and_ceiling(screen)
        
        # Z-buffer for sprite rendering
        z_buffer = [float('inf')] * self.screen_width
        
        # Calculate the virtual camera position, offset from the player's actual position
        offset = 0.5  # Render from half a tile behind the player
        cam_x = self.player_x - offset * math.cos(self.player_angle)
        cam_y = self.player_y - offset * math.sin(self.player_angle)
        
        # Cast one ray for each column of the screen
        for x in range(self.screen_width):
            # Calculate the ray angle
            ray_angle = self.player_angle - self.fov / 2 + (x / self.screen_width) * self.fov
            
            # Normalize the angle
            ray_angle = ray_angle % (2 * math.pi)
            
            # Cast the ray from the virtual camera position
            distance, wall_type, hit_x, hit_y, side, map_x, map_y = self.cast_single_ray(ray_angle, cam_x, cam_y)
            
            # Correct for fisheye effect
            distance *= math.cos(ray_angle - self.player_angle)
            z_buffer[x] = distance
            
            # Calculate wall height based on the distance to the projection plane.
            # This ensures the projection is geometrically correct.
            wall_height = max(1, (self.projection_plane_dist / distance)) if distance > 0 else self.screen_height
            
            # Use dungeon wall texture for all walls
            texture = self.texture_manager.get_texture("dungeon_wall")
            
            # Draw textured wall slice if texture is available
            if wall_type > 0 and texture:
                # Calculate wall position - centered between ceiling and floor
                wall_top = (self.screen_height - wall_height) // 2
                wall_bottom = wall_top + wall_height
                
                # Calculate texture coordinate based on which side was hit
                # side = 0 means x-side (east/west wall faces)
                # side = 1 means y-side (north/south wall faces)
                if side == 0:  # Hit east/west wall face (use Y coordinate for texture)
                    tex_coord = hit_y - math.floor(hit_y) if hit_y is not None else 0
                else:  # Hit north/south wall face (use X coordinate for texture)
                    tex_coord = hit_x - math.floor(hit_x) if hit_x is not None else 0
                    
                # Map to texture pixel coordinate
                tex_x = int(tex_coord * (self.tex_width - 1))
                
                # Ensure tex_x is within bounds
                tex_x = max(0, min(self.tex_width - 1, tex_x))
                
                # Extract a single column from the texture
                tex_column = texture.subsurface((tex_x, 0, 1, self.tex_height))
                
                # Scale the texture column to match the wall height
                scaled_column = pygame.transform.scale(tex_column, (1, int(wall_height)))
                
                # Apply lighting
                light_level = self.game_map.light_map[map_y][map_x]
                darkness = pygame.Surface(scaled_column.get_size()).convert_alpha()
                darkness.fill((0, 0, 0, 255 * (1 - light_level)))
                
                screen.blit(scaled_column, (x, wall_top))
                screen.blit(darkness, (x, wall_top))
                
            elif wall_type > 0:
                # Fallback to solid color if texture not available
                color = self.wall_colors.get(wall_type, (100, 100, 110))
                
                # Apply lighting
                light_level = self.game_map.light_map[map_y][map_x]
                color = (int(color[0] * light_level), int(color[1] * light_level), int(color[2] * light_level))
                
                wall_top = (self.screen_height - wall_height) // 2
                wall_bottom = wall_top + wall_height
                pygame.draw.line(screen, color, (x, wall_top), (x, wall_bottom))
            else:
                # Draw empty space (don't draw anything)
                pass
        
        self.render_sprites(screen, z_buffer)
        
    def render_floor_and_ceiling(self, screen):
        """Render textured floor and ceiling using raycasting technique"""
        floor_texture = self.texture_manager.get_texture("dungeon_floor")
        ceiling_color = (30, 30, 40) # Keep ceiling as a solid color for now

        # Draw ceiling
        pygame.draw.rect(screen, ceiling_color, (0, 0, self.screen_width, self.screen_height // 2))

        if not floor_texture:
            # Fallback to solid color if texture is not available
            player_map_x = int(self.player_x)
            player_map_y = int(self.player_y)
            light_level = self.game_map.light_map[player_map_y][player_map_x]
            floor_color = (50, 50, 50)
            lit_floor_color = (int(floor_color[0] * light_level), int(floor_color[1] * light_level), int(floor_color[2] * light_level))
            pygame.draw.rect(screen, lit_floor_color, (0, self.screen_height // 2, self.screen_width, self.screen_height // 2))
            return

        # Render textured floor
        for y in range(self.screen_height // 2, self.screen_height):
            # Ray direction for the leftmost and rightmost ray
            ray_dir_x0 = math.cos(self.player_angle - self.fov / 2)
            ray_dir_y0 = math.sin(self.player_angle - self.fov / 2)
            ray_dir_x1 = math.cos(self.player_angle + self.fov / 2)
            ray_dir_y1 = math.sin(self.player_angle + self.fov / 2)

            # Vertical position of the pixel on the screen
            p = y - self.screen_height // 2

            if p == 0:
                continue
            
            # Vertical position of the camera.
            pos_z = 0.5 * self.screen_height

            # Horizontal distance from the camera to the floor for the current row.
            # 0.5 is the z position of the camera.
            row_distance = pos_z / p if p != 0 else float('inf')

            # Calculate the real world step vector we have to add for each x (parallel to camera plane)
            # adding step_x to floor_x and step_y to floor_y for each pixel
            step_x = row_distance * (ray_dir_x1 - ray_dir_x0) / self.screen_width
            step_y = row_distance * (ray_dir_y1 - ray_dir_y0) / self.screen_width

            # Real world coordinates of the leftmost column. This will be updated as we step to the right.
            floor_x = self.player_x + row_distance * ray_dir_x0
            floor_y = self.player_y + row_distance * ray_dir_y0

            for x in range(self.screen_width):
                # The cell coord is simply got from the integer parts of floor_x and floor_y
                cell_x = int(floor_x)
                cell_y = int(floor_y)

                # Get the texture coordinate from the fractional part
                tx = int(self.tex_width * (floor_x - cell_x)) & (self.tex_width - 1)
                ty = int(self.tex_height * (floor_y - cell_y)) & (self.tex_height - 1)

                floor_x += step_x
                floor_y += step_y

                # Get the color from the texture
                color = floor_texture.get_at((tx, ty))

                # Apply lighting
                if 0 <= cell_x < self.map_width and 0 <= cell_y < self.map_height:
                    light_level = self.game_map.light_map[cell_y][cell_x]
                    color = (int(color[0] * light_level), int(color[1] * light_level), int(color[2] * light_level))
                
                # Draw the pixel
                screen.set_at((x, y), color)
    
    def cast_single_ray(self, ray_angle, player_x, player_y):
        """Cast a single ray and return the distance to the first wall hit, the wall type, and hit coordinates"""
        # Ray direction
        ray_dir_x = math.cos(ray_angle)
        ray_dir_y = math.sin(ray_angle)
        
        # Player's map position
        map_x = int(player_x)
        map_y = int(player_y)
        
        # Length of ray from current position to next x or y-side
        delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else float('inf')
        delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else float('inf')
        
        # Direction to step in x or y direction (either +1 or -1)
        step_x = 1 if ray_dir_x >= 0 else -1
        step_y = 1 if ray_dir_y >= 0 else -1
        
        # Length of ray from one side to next in map
        if ray_dir_x < 0:
            side_dist_x = (player_x - map_x) * delta_dist_x
        else:
            side_dist_x = (map_x + 1.0 - player_x) * delta_dist_x
            
        if ray_dir_y < 0:
            side_dist_y = (player_y - map_y) * delta_dist_y
        else:
            side_dist_y = (map_y + 1.0 - player_y) * delta_dist_y
        
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
            perp_wall_dist = (map_x - player_x + (1 - step_x) / 2) / ray_dir_x
            # Calculate exact hit position
            hit_y = player_y + perp_wall_dist * ray_dir_y
            hit_x = map_x if ray_dir_x > 0 else map_x + 1
        else:
            perp_wall_dist = (map_y - player_y + (1 - step_y) / 2) / ray_dir_y
            # Calculate exact hit position
            hit_x = player_x + perp_wall_dist * ray_dir_x
            hit_y = map_y if ray_dir_y > 0 else map_y + 1
            
        return perp_wall_dist, self.map_data[map_y][map_x] if hit else 0, hit_x, hit_y, side, map_x, map_y

    def render_sprites(self, screen, z_buffer):
        """Render sprites (enemies, items, etc.)"""
        entities = self.game_map.entities
        
        entities.sort(key=lambda e: ((self.player_x - e.x)**2 + (self.player_y - e.y)**2), reverse=True)
        
        for entity in entities:
            if entity.sprite and self.texture_manager.get_sprite(entity.sprite):
                sprite = self.texture_manager.get_sprite(entity.sprite)
                
                sprite_x = (entity.x + 0.5) - self.player_x
                sprite_y = (entity.y + 0.5) - self.player_y
                
                # transform_x is depth, transform_y is horizontal position on camera plane
                depth = math.cos(self.player_angle) * sprite_x + math.sin(self.player_angle) * sprite_y
                horizontal_pos = -math.sin(self.player_angle) * sprite_x + math.cos(self.player_angle) * sprite_y
                
                # Sprite is in front of player
                if depth > 0.5: # Use a threshold to avoid clipping
                    # Project sprite to screen
                    sprite_screen_x = int((self.screen_width / 2) * (1 + horizontal_pos / depth))
                    
                    # Calculate sprite height and width. Use projection_plane_dist for correct scaling.
                    sprite_height = abs(int(self.projection_plane_dist / depth))
                    # Maintain aspect ratio
                    aspect_ratio = sprite.get_width() / sprite.get_height() if sprite.get_height() > 0 else 1
                    sprite_width = int(sprite_height * aspect_ratio)
                    
                    # Calculate drawing boundaries on screen
                    draw_start_y = self.screen_height // 2 - sprite_height // 2
                    draw_end_y = self.screen_height // 2 + sprite_height // 2
                    draw_start_x = sprite_screen_x - sprite_width // 2
                    draw_end_x = sprite_screen_x + sprite_width // 2
                    
                    # Draw the sprite column by column
                    for stripe in range(draw_start_x, draw_end_x):
                        # Check if stripe is on screen and in front of a wall
                        if 0 <= stripe < self.screen_width and depth < z_buffer[stripe]:
                            # Calculate texture x coordinate
                            tex_x = int((stripe - draw_start_x) * sprite.get_width() / sprite_width) if sprite_width > 0 else 0
                            
                            if 0 <= tex_x < sprite.get_width():
                                # Get the column of the texture
                                tex_column = sprite.subsurface(tex_x, 0, 1, sprite.get_height())
                                # Scale it to the correct height
                                scaled_column = pygame.transform.scale(tex_column, (1, sprite_height))
                                
                                # Apply lighting
                                light_level = self.game_map.light_map[int(entity.y)][int(entity.x)]
                                
                                # Create a copy to avoid modifying the original texture column
                                lit_column = scaled_column.copy()
                                
                                # Create a lighting color
                                light_color = (int(255 * light_level), int(255 * light_level), int(255 * light_level))
                                
                                # Apply lighting only to non-transparent pixels using multiplicative blending
                                lit_column.fill(light_color, special_flags=pygame.BLEND_MULT)

                                # Draw the column
                                screen.blit(lit_column, (stripe, draw_start_y))
