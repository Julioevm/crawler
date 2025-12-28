"""
Raycasting engine for the first-person view in the dungeon crawler.
Based on the technique used in Wolfenstein 3D.
"""

import math
import pygame
import numpy as np
from config.constants import TEXTURE_SIZE
from game.party import Party

class Raycaster:
    def __init__(self, screen_width, screen_height, game_map, texture_manager=None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.floor_buffer = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
        self.game_map = game_map
        self.map_data = game_map.tiles
        self.transparent_tiles = {3} # Tile IDs that the raycaster can see through
        self.map_width = len(self.map_data[0])
        self.map_height = len(self.map_data)
        self.texture_manager = texture_manager
        
        # Party properties (center of the grid cell)
        self.party_x = 1.5
        self.party_y = 1.5
        self.party_angle = 0
        
        # Rendering properties
        self.fov = math.pi * 5 / 12  # 75 degrees field of view
        # Distance to the projection plane. This is key for a correct 3D projection.
        # It is calculated based on the screen width and the field of view.
        # This replaces the arbitrary `wall_height` scaling factor.
        self.projection_plane_dist = (self.screen_width / 2) / math.tan(self.fov / 2)
        
        # Texture size
        self.tex_width = TEXTURE_SIZE
        self.tex_height = TEXTURE_SIZE
        
        # Create default textures if no texture manager provided
        if not self.texture_manager:
            from engine.texture_manager import TextureManager
            self.texture_manager = TextureManager()
            self.texture_manager.create_default_textures()
    
    def set_party_position(self, x, y):
        """Set the party's position"""
        self.party_x = x + 0.5  # Center of the cell
        self.party_y = y + 0.5  # Center of the cell
    
    def set_party_angle(self, angle):
        """Set the party's viewing angle"""
        self.party_angle = angle
    
    def cast_rays(self, screen):
        """Cast rays and render the 3D view"""
        # Render floor and ceiling first
        self.render_floor_and_ceiling(screen)
        
        # Z-buffer for sprite rendering
        z_buffer = [float('inf')] * self.screen_width
        
        # Calculate the virtual camera position, offset from the player's actual position
        offset = 0.5  # Render from half a tile behind the party
        cam_x = self.party_x - offset * math.cos(self.party_angle)
        cam_y = self.party_y - offset * math.sin(self.party_angle)
        
        # Cast one ray for each column of the screen
        for x in range(self.screen_width):
            # Calculate the ray angle
            ray_angle = self.party_angle - self.fov / 2 + (x / self.screen_width) * self.fov
            
            # Normalize the angle
            ray_angle = ray_angle % (2 * math.pi)
            
            # Cast the ray from the virtual camera position
            wall_hits = self.cast_single_ray(ray_angle, cam_x, cam_y)
            
            # Draw walls from back to front
            solid_wall_dist = float('inf')
            for distance, wall_type, hit_x, hit_y, side, map_x, map_y in sorted(wall_hits, key=lambda x: x[0], reverse=True):
                # Correct for fisheye effect
                corrected_dist = distance * math.cos(ray_angle - self.party_angle)

                # Find the closest solid wall for the z-buffer
                if wall_type not in self.transparent_tiles:
                    solid_wall_dist = min(solid_wall_dist, corrected_dist)

                # Calculate wall height based on the distance to the projection plane.
                wall_height = max(1, (self.projection_plane_dist / corrected_dist)) if corrected_dist > 0 else self.screen_height

                # Determine texture based on wall type
                if wall_type == 1:
                    texture = self.texture_manager.get_texture("dungeon_wall")
                elif wall_type == 2:
                    texture = self.texture_manager.get_texture("dungeon_door_closed")
                elif wall_type == 3:
                    texture = self.texture_manager.get_texture("dungeon_door_open")
                else:
                    texture = None

                if texture:
                    wall_top = (self.screen_height - wall_height) // 2
                    
                    if side == 0:
                        tex_coord = hit_y - math.floor(hit_y) if hit_y is not None else 0
                    else:
                        tex_coord = hit_x - math.floor(hit_x) if hit_x is not None else 0
                    
                    tex_x = int(tex_coord * (self.tex_width - 1))
                    tex_x = max(0, min(self.tex_width - 1, tex_x))
                    
                    tex_column = texture.subsurface((tex_x, 0, 1, self.tex_height))
                    scaled_column = pygame.transform.scale(tex_column, (1, int(wall_height)))

                    # Blit the scaled texture column directly to preserve transparency
                    screen.blit(scaled_column, (x, wall_top))

                    # Apply lighting by blitting a colored surface on top with a multiply blend
                    light_level = self.game_map.light_map[map_y][map_x]
                    if light_level < 1.0:
                        light_color = (int(255 * light_level), int(255 * light_level), int(255 * light_level))
                        light_surface = pygame.Surface((1, int(wall_height)), pygame.SRCALPHA)
                        light_surface.fill(light_color)
                        screen.blit(light_surface, (x, wall_top), special_flags=pygame.BLEND_MULT)
            
            z_buffer[x] = solid_wall_dist
        
        self.render_sprites(screen, z_buffer)
        
    def render_floor_and_ceiling(self, screen):
        """Render textured floor and ceiling using numpy for performance."""
        floor_texture_arr = self.texture_manager.get_texture_array("dungeon_floor")
        ceil_texture_arr = self.texture_manager.get_texture_array("dungeon_ceil")

        # Pre-calculate angles
        angle_cos = math.cos(self.party_angle)
        angle_sin = math.sin(self.party_angle)
        fov_half = self.fov / 2
        
        # Ray directions for the leftmost and rightmost columns
        ray_dir_x0 = angle_cos * math.cos(-fov_half) - angle_sin * math.sin(-fov_half)
        ray_dir_y0 = angle_sin * math.cos(-fov_half) + angle_cos * math.sin(-fov_half)
        ray_dir_x1 = angle_cos * math.cos(fov_half) - angle_sin * math.sin(fov_half)
        ray_dir_y1 = angle_sin * math.cos(fov_half) + angle_cos * math.sin(fov_half)

        # Create arrays for y values for floor and ceiling
        y_floor = np.arange(self.screen_height // 2, self.screen_height)
        y_ceil = np.arange(self.screen_height // 2)

        # Calculate row distances
        p_floor = y_floor - self.screen_height / 2
        p_ceil = self.screen_height / 2 - y_ceil
        
        # Avoid division by zero
        p_floor[p_floor == 0] = 1
        p_ceil[p_ceil == 0] = 1

        row_distance_floor = (0.5 * self.screen_height) / p_floor
        row_distance_ceil = (0.5 * self.screen_height) / p_ceil

        # Calculate step vectors for floor and ceiling
        step_x_floor = row_distance_floor[:, np.newaxis] * (ray_dir_x1 - ray_dir_x0) / self.screen_width
        step_y_floor = row_distance_floor[:, np.newaxis] * (ray_dir_y1 - ray_dir_y0) / self.screen_width
        step_x_ceil = row_distance_ceil[:, np.newaxis] * (ray_dir_x1 - ray_dir_x0) / self.screen_width
        step_y_ceil = row_distance_ceil[:, np.newaxis] * (ray_dir_y1 - ray_dir_y0) / self.screen_width

        # Calculate texture world coordinates for floor and ceiling
        tex_world_x_floor = self.party_x + row_distance_floor[:, np.newaxis] * ray_dir_x0
        tex_world_y_floor = self.party_y + row_distance_floor[:, np.newaxis] * ray_dir_y0
        tex_world_x_ceil = self.party_x + row_distance_ceil[:, np.newaxis] * ray_dir_x0
        tex_world_y_ceil = self.party_y + row_distance_ceil[:, np.newaxis] * ray_dir_y0

        # Generate x-coordinates for stepping
        x_coords = np.arange(self.screen_width)

        # Calculate full texture coordinates for floor and ceiling
        full_tex_x_floor = tex_world_x_floor + x_coords * step_x_floor
        full_tex_y_floor = tex_world_y_floor + x_coords * step_y_floor
        full_tex_x_ceil = tex_world_x_ceil + x_coords * step_x_ceil
        full_tex_y_ceil = tex_world_y_ceil + x_coords * step_y_ceil

        # Get cell coordinates
        cell_x_floor = full_tex_x_floor.astype(int)
        cell_y_floor = full_tex_y_floor.astype(int)
        cell_x_ceil = full_tex_x_ceil.astype(int)
        cell_y_ceil = full_tex_y_ceil.astype(int)

        # Get texture coordinates
        tx_floor = (self.tex_width * (full_tex_x_floor - cell_x_floor)).astype(int) & (self.tex_width - 1)
        ty_floor = (self.tex_height * (full_tex_y_floor - cell_y_floor)).astype(int) & (self.tex_height - 1)
        tx_ceil = (self.tex_width * (full_tex_x_ceil - cell_x_ceil)).astype(int) & (self.tex_width - 1)
        ty_ceil = (self.tex_height * (full_tex_y_ceil - cell_y_ceil)).astype(int) & (self.tex_height - 1)

        # Get colors from textures
        floor_colors = floor_texture_arr[ty_floor, tx_floor]
        ceil_colors = ceil_texture_arr[ty_ceil, tx_ceil]

        # Apply lighting
        light_map_arr = np.array(self.game_map.light_map)
        
        # Create masks for valid coordinates
        floor_mask = (cell_x_floor >= 0) & (cell_x_floor < self.map_width) & (cell_y_floor >= 0) & (cell_y_floor < self.map_height)
        ceil_mask = (cell_x_ceil >= 0) & (cell_x_ceil < self.map_width) & (cell_y_ceil >= 0) & (cell_y_ceil < self.map_height)

        # Get light levels, using ambient light as a fallback
        light_levels_floor = np.full(floor_mask.shape, self.game_map.ambient_light)
        light_levels_ceil = np.full(ceil_mask.shape, self.game_map.ambient_light)
        
        light_levels_floor[floor_mask] = light_map_arr[cell_y_floor[floor_mask], cell_x_floor[floor_mask]]
        light_levels_ceil[ceil_mask] = light_map_arr[cell_y_ceil[ceil_mask], cell_x_ceil[ceil_mask]]

        # Apply lighting to colors
        floor_colors = (floor_colors * light_levels_floor[:, :, np.newaxis]).astype(np.uint8)
        ceil_colors = (ceil_colors * light_levels_ceil[:, :, np.newaxis]).astype(np.uint8)

        # Fill the buffer
        self.floor_buffer[self.screen_height // 2:, :, :] = floor_colors
        self.floor_buffer[:self.screen_height // 2, :, :] = ceil_colors

        # Blit the buffer to the screen, transposing the array to match screen dimensions
        pygame.surfarray.blit_array(screen, self.floor_buffer.transpose(1, 0, 2))
    
    def cast_single_ray(self, ray_angle, party_x, party_y):
        """
        Cast a single ray and return a list of all walls hit, including transparent ones.
        """
        ray_dir_x = math.cos(ray_angle)
        ray_dir_y = math.sin(ray_angle)
        map_x, map_y = int(party_x), int(party_y)
        delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else float('inf')
        delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else float('inf')
        step_x = 1 if ray_dir_x >= 0 else -1
        step_y = 1 if ray_dir_y >= 0 else -1

        if ray_dir_x < 0:
            side_dist_x = (party_x - map_x) * delta_dist_x
        else:
            side_dist_x = (map_x + 1.0 - party_x) * delta_dist_x
        if ray_dir_y < 0:
            side_dist_y = (party_y - map_y) * delta_dist_y
        else:
            side_dist_y = (map_y + 1.0 - party_y) * delta_dist_y

        hits = []
        max_dist = 20  # Maximum distance to cast rays

        while True:
            side = 0 if side_dist_x < side_dist_y else 1
            if side == 0:
                dist = side_dist_x
                side_dist_x += delta_dist_x
                map_x += step_x
            else:
                dist = side_dist_y
                side_dist_y += delta_dist_y
                map_y += step_y

            if dist > max_dist:
                break

            if 0 <= map_x < self.map_width and 0 <= map_y < self.map_height:
                wall_type = self.map_data[map_y][map_x]
                if wall_type > 0:
                    if side == 0:
                        perp_wall_dist = (map_x - party_x + (1 - step_x) / 2) / ray_dir_x
                        hit_y = party_y + perp_wall_dist * ray_dir_y
                        hit_x = map_x + 0.5
                    else:
                        perp_wall_dist = (map_y - party_y + (1 - step_y) / 2) / ray_dir_y
                        hit_x = party_x + perp_wall_dist * ray_dir_x
                        hit_y = map_y + 0.5
                    
                    hits.append((perp_wall_dist, wall_type, hit_x, hit_y, side, map_x, map_y))

                    if wall_type not in self.transparent_tiles:
                        break # Hit a solid wall, stop casting
            else:
                break # Ray went out of bounds
        
        return hits

    def render_sprites(self, screen, z_buffer):
        """Render sprites (enemies, items, etc.)"""
        entities = [e for e in self.game_map.entities if not isinstance(e, Party)]
        
        entities.sort(key=lambda e: ((self.party_x - e.x)**2 + (self.party_y - e.y)**2), reverse=True)
        
        for entity in entities:
            if entity.sprite and self.texture_manager.get_sprite(entity.sprite):
                sprite = self.texture_manager.get_sprite(entity.sprite)
                
                sprite_x = (entity.x + 0.5) - self.party_x
                sprite_y = (entity.y + 0.5) - self.party_y
                
                # transform_x is depth, transform_y is horizontal position on camera plane
                depth = math.cos(self.party_angle) * sprite_x + math.sin(self.party_angle) * sprite_y
                horizontal_pos = -math.sin(self.party_angle) * sprite_x + math.cos(self.party_angle) * sprite_y
                
                # Sprite is in front of party
                if depth > 0.5: # Use a threshold to avoid clipping
                    # Project sprite to screen
                    sprite_screen_x = int((self.screen_width / 2) * (1 + horizontal_pos / depth))
                    
                    # Calculate sprite height and width. Use projection_plane_dist for correct scaling.
                    sprite_height = abs(int(self.projection_plane_dist / depth))
                    # Maintain aspect ratio
                    aspect_ratio = sprite.get_width() / sprite.get_height() if sprite.get_height() > 0 else 1
                    sprite_width = int(sprite_height * aspect_ratio)
                    
                    # Calculate drawing boundaries on screen
                    if getattr(entity, "render_on_floor", False):
                        draw_start_y = self.screen_height // 2 + sprite_height // 2 - sprite_height
                    elif getattr(entity, "render_on_ceiling", False):
                        draw_start_y = self.screen_height // 2 - sprite_height // 2
                    else:
                        draw_start_y = self.screen_height // 2 - sprite_height // 2
                    
                    draw_end_y = draw_start_y + sprite_height
                    draw_start_x = sprite_screen_x - sprite_width // 2
                    draw_end_x = sprite_screen_x + sprite_width // 2
                    
                    # Scale the entire sprite once
                    scaled_sprite = pygame.transform.scale(sprite, (sprite_width, sprite_height))
                    
                    # Apply lighting
                    light_level = self.game_map.light_map[int(entity.y)][int(entity.x)]
                    light_color = (int(255 * light_level), int(255 * light_level), int(255 * light_level))
                    
                    lit_sprite = scaled_sprite.copy()
                    lit_sprite.fill(light_color, special_flags=pygame.BLEND_MULT)

                    # Draw the sprite column by column, but from the pre-scaled surface
                    for stripe in range(draw_start_x, draw_end_x):
                        # Check if stripe is on screen and in front of a wall
                        if 0 <= stripe < self.screen_width and depth < z_buffer[stripe]:
                            # Calculate texture x coordinate
                            tex_x = stripe - draw_start_x
                            
                            # Draw the column from the scaled and lit sprite
                            screen.blit(lit_sprite, (stripe, draw_start_y), (tex_x, 0, 1, sprite_height))
