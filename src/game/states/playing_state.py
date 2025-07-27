import math
import json
from pygame.locals import *

from .base_state import BaseState
from engine.raycaster import Raycaster
from engine.texture_manager import TextureManager
from entities.character import Character
from game.party import Party
from entities.enemy import Enemy
from entities.enemy_group import EnemyGroup
from entities.door import Door
from entities.potion import Potion
from entities.spell import Spell
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

        for y, row in enumerate(map_data):
            for x, tile in enumerate(row):
                if tile == 2:
                    self.game_map.add_entity(Door(x, y))

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
                    item = Potion(item_data["name"], item_data["description"], item_data["heal_amount"])
                elif item_data["type"] == "weapon":
                    item = Weapon(item_data["name"], item_data["description"], item_data["attack_bonus"])
                self.party.add_to_inventory(item)
                if isinstance(item, Weapon) and not character.equipped_weapon:
                    character.equip_weapon(item)
            for spell_data in character_data.get("spellbook", []):
                spell = Spell(
                    spell_data["name"],
                    spell_data["description"],
                    spell_data["mp_cost"],
                    spell_data["effect"],
                    spell_data.get("target_type", "enemy")
                )
                character.learn_spell(spell)
            self.party.add_character(character)

        for group_data in level_data.get("enemy_groups", []):
            enemies = []
            for enemy_data in group_data["enemies"]:
                enemy = Enemy(
                    group_data["x"], group_data["y"], enemy_data["name"],
                    enemy_data["hp"], enemy_data["attack"], enemy_data["defense"],
                    enemy_data["sprite"],
                    enemy_data.get("morale", 100)
                )
                enemies.append(enemy)
            enemy_group = EnemyGroup(group_data["x"], group_data["y"], enemies)
            self.game_map.add_entity(enemy_group)

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
        move_direction = None
        is_strafe = False

        if event.key == K_w or event.key == K_UP:
            dx = math.cos(self.party.angle)
            dy = math.sin(self.party.angle)
            move_direction = "forward"
        elif event.key == K_s or event.key == K_DOWN:
            dx = -math.cos(self.party.angle)
            dy = -math.sin(self.party.angle)
            move_direction = "backward"
        elif event.key == K_a:
            dx = math.cos(self.party.angle - math.pi/2)
            dy = math.sin(self.party.angle - math.pi/2)
            move_direction = "left"
            is_strafe = True
        elif event.key == K_d:
            dx = math.cos(self.party.angle + math.pi/2)
            dy = math.sin(self.party.angle + math.pi/2)
            move_direction = "right"
            is_strafe = True
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

        if dx != 0 or dy != 0:
            target_x = int(self.party.x + round(dx))
            target_y = int(self.party.y + round(dy))

            # Check for door interaction before other checks
            if self.game_map.tiles[target_y][target_x] == 2:
                door = next((e for e in self.game_map.get_entities_at(target_x, target_y) if isinstance(e, Door)), None)
                if door:
                    door.interact(self.game_map)
                    self.messages.append("You open the door.")
                    moved = True
            else:
                entities_at_position = self.game_map.get_entities_at(target_x, target_y)
                enemy_group = next((e for e in entities_at_position if isinstance(e, EnemyGroup) and e.is_alive()), None)

                if enemy_group:
                    moved = True
                    new_state = CombatState(self.game, self.party, enemy_group.enemies, self.combat_manager)
                    self.game.push_state(new_state)
                    self.game_map.remove_entity(enemy_group)
                elif self.game_map.is_walkable(target_x, target_y) and (int(self.party.x) != target_x or int(self.party.y) != target_y):
                    self.party.x = target_x
                    self.party.y = target_y
                    moved = True
                    self.game_map.update_light_map()
                    if is_strafe:
                        self.messages.append(f"You strafe {move_direction}")
                    else:
                        self.messages.append(f"You move {move_direction}")
                else:
                    moved = True
                    self.messages.append("That way is blocked.")

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