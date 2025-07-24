#!/usr/bin/env python3
"""
Main entry point for the Crawler game.
"""

import pygame
import sys
import math
from pygame.locals import *
from engine.raycaster import Raycaster
from engine.texture_manager import TextureManager
from entities.player import Player
from entities.enemy import Enemy
from entities.potion import Potion
from entities.weapon import Weapon
from game.game_map import GameMap
from game.turn_manager import TurnManager
from game.combat_manager import CombatManager
from ui.ui import UI
from ui.inventory_ui import InventoryUI
from ui.combat_ui import CombatUI

def main():
    # Initialize pygame
    pygame.init()
    
    # Set up the display
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Crawler - First-Person Dungeon Crawler")
    
    # Define a tighter, more corridor-like map to enhance the feeling of confined spaces
    map_data = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    
    # Create the texture manager
    texture_manager = TextureManager()
    texture_manager.create_default_textures()
    
    # Create the game map
    game_map = GameMap(len(map_data[0]), len(map_data))
    game_map.tiles = map_data
    
    # Create the player
    player = Player(1, 1)
    game_map.add_entity(player)
    
    # Add some items to the player's inventory for testing
    health_potion = Potion("Health Potion", "Restores 20 HP", 20)
    strength_potion = Potion("Strength Potion", "Temporarily increases attack", 0)  # Placeholder
    sword = Weapon("Iron Sword", "A simple iron sword", 5)
    
    player.add_to_inventory(health_potion)
    player.add_to_inventory(strength_potion)
    player.add_to_inventory(sword)
    player.equip_weapon(sword)
    
    # Create some enemies
    enemy1 = Enemy(3, 3, "Goblin", 30, 8, 2)
    enemy2 = Enemy(5, 5, "Orc", 50, 12, 5)
    game_map.add_entity(enemy1)
    game_map.add_entity(enemy2)
    
    # Create the raycaster
    raycaster = Raycaster(screen_width, screen_height, map_data, texture_manager)
    raycaster.set_player_position(player.x, player.y)
    raycaster.set_player_angle(player.angle)
    
    # Create the managers
    turn_manager = TurnManager(game_map)
    combat_manager = CombatManager()
    
    # Create the UI systems
    ui = UI(screen_width, screen_height)
    inventory_ui = InventoryUI(screen_width, screen_height)
    combat_ui = CombatUI(screen_width, screen_height)
    
    # Game messages
    messages = ["Welcome to Crawler!", "WASD: Move/Strafe, QE/Arrow Keys: Turn", "Press 'I' to open inventory"]
    
    # Set up the clock for controlling frame rate
    clock = pygame.time.Clock()
    
    # Main game loop
    running = True
    waiting_for_input = True  # In turn-based, we wait for player input
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                # Handle combat UI input
                if combat_manager.in_combat:
                    combat_result = combat_ui.handle_input(event, combat_manager)
                    if combat_result:
                        if combat_result == "victory":
                            messages.append(f"You defeated the {combat_manager.current_enemy.name}!")
                            # Remove enemy from the game
                            if combat_manager.current_enemy in game_map.entities:
                                game_map.remove_entity(combat_manager.current_enemy)
                        elif combat_result == "defeat":
                            messages.append("You have been defeated! Game over.")
                            running = False
                        elif combat_result == "fled":
                            messages.append("You fled from combat.")
                # Handle inventory UI input
                elif inventory_ui.visible:
                    inventory_result = inventory_ui.handle_input(event, player)
                    if inventory_result:
                        messages.append(inventory_result)
                elif event.key == K_ESCAPE:
                    running = False
                elif event.key == K_i and not combat_manager.in_combat:
                    # Toggle inventory visibility
                    inventory_ui.toggle_visibility()
                elif turn_manager.player_turn and waiting_for_input and not inventory_ui.visible and not combat_manager.in_combat:
                    # Handle player movement and actions
                    moved = False
                    dx, dy = 0, 0
                    
                    # WASD movement - based on player's current angle
                    if event.key == K_w:  # Move forward
                        # Move in the direction the player is facing
                        dx = math.cos(player.angle)
                        dy = math.sin(player.angle)
                        messages.append("You move forward")
                    elif event.key == K_s:  # Move backward
                        # Move opposite to the direction the player is facing
                        dx = -math.cos(player.angle)
                        dy = -math.sin(player.angle)
                        messages.append("You move backward")
                    elif event.key == K_a:  # Strafe left
                        # Strafe left relative to facing direction
                        dx = math.cos(player.angle - math.pi/2)
                        dy = math.sin(player.angle - math.pi/2)
                        messages.append("You strafe left")
                    elif event.key == K_d:  # Strafe right
                        # Strafe right relative to facing direction
                        dx = math.cos(player.angle + math.pi/2)
                        dy = math.sin(player.angle + math.pi/2)
                        messages.append("You strafe right")
                    elif event.key == K_q:  # Turn left
                        player.turn_left()
                        moved = True
                        messages.append("You turn left")
                    elif event.key == K_e:  # Turn right
                        player.turn_right()
                        moved = True
                        messages.append("You turn right")
                    
                    # Arrow key movement - based on player's current angle
                    if event.key == K_UP:  # Move forward
                        # Move in the direction the player is facing
                        dx = math.cos(player.angle)
                        dy = math.sin(player.angle)
                        messages.append("You move forward")
                    elif event.key == K_DOWN:  # Move backward
                        # Move opposite to the direction the player is facing
                        dx = -math.cos(player.angle)
                        dy = -math.sin(player.angle)
                        messages.append("You move backward")
                    elif event.key == K_LEFT:  # Turn left
                        player.turn_left()
                        moved = True
                        messages.append("You turn left")
                    elif event.key == K_RIGHT:  # Turn right
                        player.turn_right()
                        moved = True
                        messages.append("You turn right")
                    
                    # If trying to move, check if it's valid (convert continuous movement to grid-based)
                    if (dx != 0 or dy != 0):
                        # Convert continuous movement to grid-based by rounding
                        target_x = int(player.x + round(dx))
                        target_y = int(player.y + round(dy))
                        
                        # Check if the target position is valid
                        if game_map.is_walkable(target_x, target_y):
                            player.x = target_x
                            player.y = target_y
                            moved = True
                            messages.append(f"Moved to ({player.x}, {player.y})")
                        
                        # Check for enemy encounters
                        entities_at_position = game_map.get_entities_at(player.x, player.y)
                        for entity in entities_at_position:
                            if isinstance(entity, Enemy) and entity.is_alive():
                                # Start combat
                                combat_log = combat_manager.start_combat(player, entity)
                                combat_ui.start_combat(player, entity)
                                messages.extend(combat_log)
                                break
                    
                    # If player made a move/action, end their turn
                    if moved and not combat_manager.in_combat:
                        raycaster.set_player_position(player.x, player.y)
                        raycaster.set_player_angle(player.angle)
                        turn_manager.end_player_turn()
                        waiting_for_input = True
        
        # Clear the screen
        screen.fill((0, 0, 0))
        
        # Render the 3D view
        raycaster.cast_rays(screen)
        
        # Draw UI
        ui.draw_player_stats(screen, player)
        ui.draw_messages(screen, messages)
        
        # Draw inventory UI if visible
        inventory_ui.draw(screen, player)
        
        # Draw combat UI if in combat
        combat_ui.draw(screen, combat_manager)
        
        # Update the display
        pygame.display.flip()
        
        # Control the frame rate
        clock.tick(60)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()