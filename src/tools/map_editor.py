import os
import sys
import json
import pygame
import pygame_gui
from pygame import Rect

# Add src to path to import game modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from engine.texture_manager import TextureManager

# Editor Constants
EDITOR_WIDTH = 1000
EDITOR_HEIGHT = 800
SIDEBAR_WIDTH = 200
GRID_SIZE = 40  # Visual size of a tile in the editor

class MapEditor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((EDITOR_WIDTH, EDITOR_HEIGHT))
        pygame.display.set_caption("Crawler Map Editor")
        self.clock = pygame.time.Clock()
        
        self.gui_manager = pygame_gui.UIManager((EDITOR_WIDTH, EDITOR_HEIGHT))
        self.texture_manager = TextureManager(assets_path="assets")
        self.texture_manager.create_default_textures()
        
        self.map_width = 12
        self.map_height = 12
        self.map_data = [[0 for _ in range(self.map_width)] for _ in range(self.map_height)]
        self.player_pos = {"x": 1, "y": 1}
        self.enemy_groups = []
        self.entities = []
        
        self.selected_tool = "wall"
        self.is_running = True
        
        self.setup_ui()
        
    def setup_ui(self):
        # Sidebar background
        self.sidebar_rect = Rect(EDITOR_WIDTH - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, EDITOR_HEIGHT)
        
        # UI Elements
        y_offset = 10
        self.wall_btn = pygame_gui.elements.UIButton(relative_rect=Rect(EDITOR_WIDTH - SIDEBAR_WIDTH + 10, y_offset, 180, 30),
                                                    text='Wall', manager=self.gui_manager)
        y_offset += 40
        self.floor_btn = pygame_gui.elements.UIButton(relative_rect=Rect(EDITOR_WIDTH - SIDEBAR_WIDTH + 10, y_offset, 180, 30),
                                                     text='Floor', manager=self.gui_manager)
        y_offset += 40
        self.door_btn = pygame_gui.elements.UIButton(relative_rect=Rect(EDITOR_WIDTH - SIDEBAR_WIDTH + 10, y_offset, 180, 30),
                                                     text='Door', manager=self.gui_manager)
        y_offset += 40
        self.player_btn = pygame_gui.elements.UIButton(relative_rect=Rect(EDITOR_WIDTH - SIDEBAR_WIDTH + 10, y_offset, 180, 30),
                                                      text='Player Start', manager=self.gui_manager)
        y_offset += 40
        self.chest_btn = pygame_gui.elements.UIButton(relative_rect=Rect(EDITOR_WIDTH - SIDEBAR_WIDTH + 10, y_offset, 180, 30),
                                                      text='Chest', manager=self.gui_manager)
        y_offset += 40
        self.enemy_btn = pygame_gui.elements.UIButton(relative_rect=Rect(EDITOR_WIDTH - SIDEBAR_WIDTH + 10, y_offset, 180, 30),
                                                      text='Enemy Group', manager=self.gui_manager)
        y_offset += 40
        self.item_btn = pygame_gui.elements.UIButton(relative_rect=Rect(EDITOR_WIDTH - SIDEBAR_WIDTH + 10, y_offset, 180, 30),
                                                      text='Item Pile', manager=self.gui_manager)
        y_offset += 40
        self.eraser_btn = pygame_gui.elements.UIButton(relative_rect=Rect(EDITOR_WIDTH - SIDEBAR_WIDTH + 10, y_offset, 180, 30),
                                                      text='Eraser', manager=self.gui_manager)
        y_offset += 40
        self.select_btn = pygame_gui.elements.UIButton(relative_rect=Rect(EDITOR_WIDTH - SIDEBAR_WIDTH + 10, y_offset, 180, 30),
                                                      text='Select', manager=self.gui_manager)
        
        y_offset += 60
        self.save_btn = pygame_gui.elements.UIButton(relative_rect=Rect(EDITOR_WIDTH - SIDEBAR_WIDTH + 10, y_offset, 180, 30),
                                                    text='Save Map', manager=self.gui_manager)
        y_offset += 40
        self.load_btn = pygame_gui.elements.UIButton(relative_rect=Rect(EDITOR_WIDTH - SIDEBAR_WIDTH + 10, y_offset, 180, 30),
                                                    text='Load Map', manager=self.gui_manager)
        y_offset += 40
        self.new_btn = pygame_gui.elements.UIButton(relative_rect=Rect(EDITOR_WIDTH - SIDEBAR_WIDTH + 10, y_offset, 180, 30),
                                                   text='New Map', manager=self.gui_manager)
        
        y_offset += 40
        self.width_up = pygame_gui.elements.UIButton(relative_rect=Rect(EDITOR_WIDTH - SIDEBAR_WIDTH + 10, y_offset, 85, 30),
                                                    text='W +', manager=self.gui_manager)
        self.width_down = pygame_gui.elements.UIButton(relative_rect=Rect(EDITOR_WIDTH - SIDEBAR_WIDTH + 105, y_offset, 85, 30),
                                                      text='W -', manager=self.gui_manager)
        y_offset += 40
        self.height_up = pygame_gui.elements.UIButton(relative_rect=Rect(EDITOR_WIDTH - SIDEBAR_WIDTH + 10, y_offset, 85, 30),
                                                     text='H +', manager=self.gui_manager)
        self.height_down = pygame_gui.elements.UIButton(relative_rect=Rect(EDITOR_WIDTH - SIDEBAR_WIDTH + 105, y_offset, 85, 30),
                                                       text='H -', manager=self.gui_manager)

    def resize_map(self, new_w, new_h):
        new_w = max(1, new_w)
        new_h = max(1, new_h)
        new_data = [[0 for _ in range(new_w)] for _ in range(new_h)]
        for y in range(min(self.map_height, new_h)):
            for x in range(min(self.map_width, new_w)):
                new_data[y][x] = self.map_data[y][x]
        self.map_data = new_data
        self.map_width = new_w
        self.map_height = new_h
        print(f"Resized map to {new_w}x{new_h}")

    def new_map(self):
        self.map_data = [[0 for _ in range(self.map_width)] for _ in range(self.map_height)]
        self.player_pos = {"x": 1, "y": 1}
        self.enemy_groups = []
        self.entities = []
        print("Created new map")

    def save_map(self):
        data = {
            "map": self.map_data,
            "player": self.player_pos,
            "enemy_groups": self.enemy_groups,
            "entities": self.entities
        }
        os.makedirs("data/maps", exist_ok=True)
        with open("data/maps/editor_test.json", 'w') as f:
            json.dump(data, f, indent=2)
        print("Map saved to data/maps/editor_test.json")

    def load_map(self, filename="data/maps/level_1.json"):
        if not os.path.exists(filename):
            return
        with open(filename, 'r') as f:
            data = json.load(f)
            self.map_data = data["map"]
            self.map_height = len(self.map_data)
            self.map_width = len(self.map_data[0])
            self.player_pos = data["player"]
            self.enemy_groups = data.get("enemy_groups", [])
            self.entities = data.get("entities", [])
        print(f"Loaded {filename}")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            
            self.gui_manager.process_events(event)
            
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.wall_btn:
                    self.selected_tool = "wall"
                elif event.ui_element == self.floor_btn:
                    self.selected_tool = "floor"
                elif event.ui_element == self.door_btn:
                    self.selected_tool = "door"
                elif event.ui_element == self.player_btn:
                    self.selected_tool = "player"
                elif event.ui_element == self.chest_btn:
                    self.selected_tool = "chest"
                elif event.ui_element == self.enemy_btn:
                    self.selected_tool = "enemy"
                elif event.ui_element == self.item_btn:
                    self.selected_tool = "item_pile"
                elif event.ui_element == self.eraser_btn:
                    self.selected_tool = "eraser"
                elif event.ui_element == self.select_btn:
                    self.selected_tool = "select"
                elif event.ui_element == self.save_btn:
                    self.save_map()
                elif event.ui_element == self.load_btn:
                    self.load_map()
                elif event.ui_element == self.new_btn:
                    self.new_map()
                elif event.ui_element == self.width_up:
                    self.resize_map(self.map_width + 1, self.map_height)
                elif event.ui_element == self.width_down:
                    self.resize_map(self.map_width - 1, self.map_height)
                elif event.ui_element == self.height_up:
                    self.resize_map(self.map_width, self.map_height + 1)
                elif event.ui_element == self.height_down:
                    self.resize_map(self.map_width, self.map_height - 1)

            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]):
                mouse_pos = pygame.mouse.get_pos()
                if mouse_pos[0] < EDITOR_WIDTH - SIDEBAR_WIDTH:
                    grid_x = mouse_pos[0] // GRID_SIZE
                    grid_y = mouse_pos[1] // GRID_SIZE
                    
                    if 0 <= grid_x < self.map_width and 0 <= grid_y < self.map_height:
                        self.apply_tool(grid_x, grid_y)

    def apply_tool(self, x, y):
        if self.selected_tool == "wall":
            self.map_data[y][x] = 1
        elif self.selected_tool == "floor":
            self.map_data[y][x] = 0
        elif self.selected_tool == "door":
            self.map_data[y][x] = 2
        elif self.selected_tool == "player":
            self.player_pos = {"x": x, "y": y}
        elif self.selected_tool == "chest":
            # Remove existing entity at this position
            self.entities = [e for e in self.entities if not (e["x"] == x and e["y"] == y)]
            self.entities.append({
                "type": "chest",
                "x": x,
                "y": y,
                "items": [
                    { "type": "potion", "name": "Health Potion", "description": "Heals 20 HP.", "heal_amount": 20 }
                ]
            })
        elif self.selected_tool == "enemy":
            # Remove existing enemy group at this position
            self.enemy_groups = [g for g in self.enemy_groups if not (g["x"] == x and g["y"] == y)]
            self.enemy_groups.append({
                "x": x,
                "y": y,
                "enemies": [
                    {
                        "name": "Goblin",
                        "hp": 30,
                        "attack": 8,
                        "defense": 2,
                        "sprite": "goblin",
                        "morale": 80
                    }
                ]
            })
        elif self.selected_tool == "item_pile":
            # Remove existing entity at this position
            self.entities = [e for e in self.entities if not (e["x"] == x and e["y"] == y)]
            self.entities.append({
                "type": "item_pile",
                "x": x,
                "y": y,
                "items": [
                    { "type": "potion", "name": "Mana Potion", "description": "Restores 10 MP.", "heal_amount": 10 }
                ]
            })
        elif self.selected_tool == "eraser":
            self.map_data[y][x] = 0
            self.entities = [e for e in self.entities if not (e["x"] == x and e["y"] == y)]
            self.enemy_groups = [g for g in self.enemy_groups if not (g["x"] == x and g["y"] == y)]
        elif self.selected_tool == "select":
             # Just find what's there and print to console for now
            found = False
            for e in self.entities:
                if e["x"] == x and e["y"] == y:
                    print(f"Selected Entity: {e['type']} at ({x}, {y}) with {len(e.get('items', []))} items")
                    found = True
            for g in self.enemy_groups:
                if g["x"] == x and g["y"] == y:
                    print(f"Selected Enemy Group at ({x}, {y}) with {len(g.get('enemies', []))} enemies")
                    found = True
            if not found:
                print(f"Tile at ({x}, {y}): {self.map_data[y][x]}")

    def draw(self):
        self.screen.fill((50, 50, 50))
        
        # Draw grid
        for y in range(self.map_height):
            for x in range(self.map_width):
                rect = Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                tile_type = self.map_data[y][x]
                
                if tile_type == 1: # Wall
                    tex = self.texture_manager.get_texture("dungeon_wall")
                elif tile_type == 2: # Door
                    tex = self.texture_manager.get_texture("dungeon_door_closed")
                else: # Floor
                    tex = self.texture_manager.get_texture("dungeon_floor")
                
                if tex:
                    scaled_tex = pygame.transform.scale(tex, (GRID_SIZE, GRID_SIZE))
                    self.screen.blit(scaled_tex, rect)
                else:
                    pygame.draw.rect(self.screen, (100, 100, 100) if tile_type == 1 else (30, 30, 30), rect)
                
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
        
        # Draw Player
        player_rect = Rect(self.player_pos["x"] * GRID_SIZE + 5, self.player_pos["y"] * GRID_SIZE + 5, GRID_SIZE - 10, GRID_SIZE - 10)
        pygame.draw.circle(self.screen, (0, 255, 0), player_rect.center, GRID_SIZE // 3)
        
        # Draw Enemies
        for group in self.enemy_groups:
            rect = Rect(group["x"] * GRID_SIZE + 5, group["y"] * GRID_SIZE + 5, GRID_SIZE - 10, GRID_SIZE - 10)
            sprite_name = group["enemies"][0]["sprite"] if group["enemies"] else "goblin"
            sprite = self.texture_manager.get_sprite(sprite_name)
            if sprite:
                scaled_sprite = pygame.transform.scale(sprite, (GRID_SIZE - 10, GRID_SIZE - 10))
                self.screen.blit(scaled_sprite, rect)
            else:
                pygame.draw.rect(self.screen, (255, 0, 0), rect)

        # Draw Entities (Chests, Item Piles)
        for entity in self.entities:
            rect = Rect(entity["x"] * GRID_SIZE + 5, entity["y"] * GRID_SIZE + 5, GRID_SIZE - 10, GRID_SIZE - 10)
            sprite_name = "chest" if entity["type"] == "chest" else "item_pile"
            sprite = self.texture_manager.get_sprite(sprite_name)
            if sprite:
                scaled_sprite = pygame.transform.scale(sprite, (GRID_SIZE - 10, GRID_SIZE - 10))
                self.screen.blit(scaled_sprite, rect)
            else:
                color = (255, 255, 0) if entity["type"] == "chest" else (0, 255, 255)
                pygame.draw.rect(self.screen, color, rect)

        # Draw sidebar
        pygame.draw.rect(self.screen, (40, 40, 40), self.sidebar_rect)
        
        # Show selected tool
        font = pygame.font.SysFont(None, 24)
        tool_text = font.render(f"Tool: {self.selected_tool}", True, (255, 255, 255))
        self.screen.blit(tool_text, (EDITOR_WIDTH - SIDEBAR_WIDTH + 10, EDITOR_HEIGHT - 30))
        
        self.gui_manager.draw_ui(self.screen)
        
        pygame.display.flip()

    def run(self):
        while self.is_running:
            time_delta = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.gui_manager.update(time_delta)
            self.draw()
        pygame.quit()

if __name__ == "__main__":
    editor = MapEditor()
    editor.run()
