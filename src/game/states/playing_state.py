import math
import json
from pygame.locals import *

from .base_state import BaseState
from engine.raycaster import Raycaster
from engine.texture_manager import TextureManager
from entities.character import Character
from game.party import Party
from entities.enemy import Enemy
from entities.potion import Potion
from entities.weapon import Weapon
from game.game_map import GameMap
from game.turn_manager import TurnManager
from game.combat_manager import CombatManager
from ui.combat_ui import CombatUI
from ui.minimap_ui import MinimapUI
from ui.game_gui import GameGUI
from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from .inventory_state import InventoryState
from .combat_state import CombatState

class PlayingState(BaseState):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.texture_manager = TextureManager()
        self.texture_manager.create_default_textures()
        self.load_level("data/maps/level_1.json")

        self.raycaster = Raycaster(SCREEN_WIDTH, SCREEN_HEIGHT, self.game_map, self.texture_manager)
        self.raycaster.set_party_position(self.party.x, self.party.y)
        self.raycaster.set_party_angle(self.party.angle)

        self.turn_manager = TurnManager(self.game_map)
        self.combat_manager = CombatManager()

        self.combat_ui = CombatUI(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.minimap_ui = MinimapUI(SCREEN_WIDTH, SCREEN_HEIGHT, self.game_map.width, self.game_map.height)
        self.game_gui = GameGUI(self.texture_manager)

        self.messages = ["Welcome to Crawler!", "WASD: Move/Strafe, QE/Arrow Keys: Turn", "Press 'I' to open inventory", "Press 'TAB' to show minimap"]
        self.game_map.update_light_map()
        self.waiting_for_input = True

    def load_level(self, file_path):
        with open(file_path, 'r') as f:
            level_data = json.load(f)

        map_data = level_data["map"]
        self.game_map = GameMap(len(map_data[0]), len(map_data))
        self.game_map.tiles = map_data

        player_data = level_data["player"]
        self.party = Party(player_data["x"], player_data["y"])
        self.game_map.add_entity(self.party)

        with open("data/party.json", 'r') as f:
            party_data = json.load(f)

        for character_data in party_data["characters"]:
            character = Character(
                character_data["name"],
                character_data["hp"],
                character_data["mp"],
                character_data["attack"],
                character_data["defense"],
                character_data.get("portrait")
            )
            for item_data in character_data.get("items", []):
                if item_data["type"] == "potion":
                    item = Potion(item_data["name"], item_data["description"], item_data["value"])
                elif item_data["type"] == "weapon":
                    item = Weapon(item_data["name"], item_data["description"], item_data["attack_bonus"])
                self.party.add_to_inventory(item)
                if isinstance(item, Weapon) and not character.equipped_weapon:
                    character.equip_weapon(item)
            self.party.add_character(character)

        for entity_data in level_data.get("entities", []):
            if entity_data["type"] == "enemy":
                enemy = Enemy(
                    entity_data["x"], entity_data["y"], entity_data["name"],
                    entity_data["hp"], entity_data["attack"], entity_data["defense"],
                    entity_data["sprite"]
                )
                self.game_map.add_entity(enemy)

    def get_event(self, event):
        self.game_gui.process_events(event)
        if event.type == KEYDOWN:
            if self.minimap_ui.handle_input(event):
                return

            if event.key == K_i and not self.combat_manager.in_combat:
                new_state = InventoryState(self.party)
                self.game.push_state(new_state)
            elif event.key == K_TAB and not self.combat_manager.in_combat:
                self.minimap_ui.toggle_visibility()
            elif self.turn_manager.player_turn and self.waiting_for_input and not self.combat_manager.in_combat:
                self.handle_party_input(event)

    def handle_party_input(self, event):
        moved = False
        dx, dy = 0, 0

        if event.key == K_w or event.key == K_UP:
            dx = math.cos(self.party.angle)
            dy = math.sin(self.party.angle)
            self.messages.append("You move forward")
        elif event.key == K_s or event.key == K_DOWN:
            dx = -math.cos(self.party.angle)
            dy = -math.sin(self.party.angle)
            self.messages.append("You move backward")
        elif event.key == K_a:
            dx = math.cos(self.party.angle - math.pi/2)
            dy = math.sin(self.party.angle - math.pi/2)
            self.messages.append("You strafe left")
        elif event.key == K_d:
            dx = math.cos(self.party.angle + math.pi/2)
            dy = math.sin(self.party.angle + math.pi/2)
            self.messages.append("You strafe right")
        elif event.key == K_q or event.key == K_LEFT:
            self.party.turn_left()
            moved = True
            self.messages.append("You turn left")
        elif event.key == K_e or event.key == K_RIGHT:
            self.party.turn_right()
            moved = True
            self.messages.append("You turn right")
        elif event.key == K_SPACE:
            moved = True
            self.messages.append("You wait for a turn")

        if (dx != 0 or dy != 0):
            target_x = int(self.party.x + round(dx))
            target_y = int(self.party.y + round(dy))

            if self.game_map.is_walkable(target_x, target_y):
                if int(self.party.x) != target_x or int(self.party.y) != target_y:
                    self.party.x = target_x
                    self.party.y = target_y
                    moved = True
                    self.game_map.update_light_map()
                else:
                    self.party.x = target_x
                    self.party.y = target_y
                    moved = True
            
            entities_at_position = self.game_map.get_entities_at(self.party.x, self.party.y)
            for entity in entities_at_position:
                if isinstance(entity, Enemy) and entity.is_alive():
                    new_state = CombatState(self.game, self.party, entity, self.combat_manager)
                    self.game.push_state(new_state)
                    break

        if moved and not self.combat_manager.in_combat:
            self.raycaster.set_party_position(self.party.x, self.party.y)
            self.raycaster.set_party_angle(self.party.angle)
            self.turn_manager.end_player_turn()
            self.waiting_for_input = True

    def update(self, time_delta):
        self.game_gui.update(time_delta)

    def draw(self, screen, clock):
        if not self.minimap_ui.visible:
            self.raycaster.cast_rays(screen)
        
        # self.ui.draw_fps(screen, clock.get_fps())
        
        self.minimap_ui.draw(screen, self.game_map, self.party)
        self.game_gui.update_message_log(self.messages)
        self.game_gui.update_compass(self.party.facing)
        self.game_gui.draw_minimap(screen, self.game_map, self.party)
        self.game_gui.update_party_stats(self.party)
        self.game_gui.draw(screen)