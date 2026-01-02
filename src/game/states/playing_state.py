import math
import json

from .base_state import BaseState
from engine.raycaster import Raycaster
from entities.character import Character
from game.party import Party
from entities.enemy import Enemy
from entities.enemy_group import EnemyGroup
from entities.door import Door
from entities.potion import Potion
from entities.spell import Spell
from entities.weapon import Weapon
from entities.item import Item
from entities.chest import Chest
from entities.item_pile import ItemPile
from game.game_map import GameMap
from game.turn_manager import TurnManager
from game.combat_manager import CombatManager
from ui.minimap_ui import MinimapUI

from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from .inventory_state import InventoryState
from .combat_state import CombatState
from .loot_state import LootState
from pygame import KEYDOWN, K_w, K_a, K_s, K_d, K_q, K_e, K_i, K_SPACE, K_TAB, K_UP, K_DOWN, K_LEFT, K_RIGHT

class PlayingState(BaseState):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.texture_manager = self.game.texture_manager
        self.game_gui = self.game.game_gui
        self.texture_manager.create_default_textures()
        self.load_level("data/maps/level_1.json")

        self.raycaster = Raycaster(SCREEN_WIDTH, SCREEN_HEIGHT, self.game_map, self.texture_manager)
        self.raycaster.set_party_position(self.party.x, self.party.y)
        self.raycaster.set_party_angle(self.party.angle)

        self.turn_manager = TurnManager(self.game_map)
        self.combat_manager = CombatManager(self.game_gui)

        self.minimap_ui = MinimapUI(SCREEN_WIDTH, SCREEN_HEIGHT, self.game_map.width, self.game_map.height)

        self.game_gui.add_message("Welcome to Crawler!")
        self.game_gui.add_message("WASD: Move/Strafe, QE/Arrow Keys: Turn")
        self.game_gui.add_message("Press 'I' to open inventory")
        self.game_gui.add_message("Press 'TAB' to show minimap")
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
                item = self._create_item(item_data)
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

        for entity_data in level_data.get("entities", []):
            entity_type = entity_data.get("type")
            x = entity_data.get("x")
            y = entity_data.get("y")
            
            items = [self._create_item(item_data) for item_data in entity_data.get("items", [])]

            if entity_type == "chest":
                chest = Chest(x, y,
                               items=items,
                               trapped=entity_data.get("trapped", False),
                               locked=entity_data.get("locked", False))
                self.game_map.add_entity(chest)
            elif entity_type == "item_pile":
                item_pile = ItemPile(x, y, items=items)
                self.game_map.add_entity(item_pile)

    def _create_item(self, item_data):
        if item_data["type"] == "potion":
            return Potion(item_data["name"], item_data["description"], item_data["heal_amount"])
        elif item_data["type"] == "weapon":
            return Weapon(item_data["name"], item_data["description"], item_data["attack_bonus"])
        else:
            return Item(item_data["name"], item_data["description"], item_data.get("type", "misc"))

    def get_event(self, event):
        if self.game_gui.last_action and "interaction" in self.game_gui.last_action:
            self.handle_interaction(self.game_gui.last_action["interaction"])
            return

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
        elif event.key == K_s or event.key == K_DOWN:
            dx = -math.cos(self.party.angle)
            dy = -math.sin(self.party.angle)
        elif event.key == K_a:
            dx = math.cos(self.party.angle - math.pi/2)
            dy = math.sin(self.party.angle - math.pi/2)
        elif event.key == K_d:
            dx = math.cos(self.party.angle + math.pi/2)
            dy = math.sin(self.party.angle + math.pi/2)
        elif event.key == K_q or event.key == K_LEFT:
            self.party.turn_left()
            moved = True
        elif event.key == K_e or event.key == K_RIGHT:
            self.party.turn_right()
            moved = True
        elif event.key == K_SPACE:
            moved = True
            self.game_gui.add_message("You wait for a turn")

        if dx != 0 or dy != 0:
            target_x = int(self.party.x + round(dx))
            target_y = int(self.party.y + round(dy))

            # Check for door interaction before other checks
            if self.game_map.tiles[target_y][target_x] == 2:
                door = next((e for e in self.game_map.get_entities_at(target_x, target_y) if isinstance(e, Door)), None)
                if door:
                    door.interact(self.game_map)
                    self.game_gui.add_message("You open the door.")
                    moved = True
            else:
                entities_at_position = self.game_map.get_entities_at(target_x, target_y)
                enemy_group = next((e for e in entities_at_position if isinstance(e, EnemyGroup) and e.is_alive()), None)
                chest = next((e for e in entities_at_position if isinstance(e, Chest)), None)
                item_pile = next((e for e in entities_at_position if isinstance(e, ItemPile)), None)

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
                else:
                    moved = True
                    self.game_gui.add_message("That way is blocked.")

        if moved and not self.combat_manager.in_combat:
            self.raycaster.set_party_position(self.party.x, self.party.y)
            self.raycaster.set_party_angle(self.party.angle)
            self.turn_manager.end_player_turn()
            self.waiting_for_input = True

    def update(self, time_delta):
        # Check for entities in front of the player
        target_x = int(self.party.x + math.cos(self.party.angle))
        target_y = int(self.party.y + math.sin(self.party.angle))
        entities_in_front = self.game_map.get_entities_at(target_x, target_y)
        
        # Check for entities at the player's feet
        entities_at_feet = self.game_map.get_entities_at(int(self.party.x), int(self.party.y))

        interaction_entity = None
        for entity in entities_in_front:
            if isinstance(entity, (Chest, ItemPile)):
                interaction_entity = entity
                break
        
        if not interaction_entity:
            for entity in entities_at_feet:
                if isinstance(entity, (Chest, ItemPile)):
                    interaction_entity = entity
                    break

        if interaction_entity:
            self.game_gui.show_interaction_buttons(interaction_entity)
        else:
            self.game_gui.hide_interaction_buttons()

    def handle_interaction(self, action):
        target_x = int(self.party.x + math.cos(self.party.angle))
        target_y = int(self.party.y + math.sin(self.party.angle))
        entities_in_front = self.game_map.get_entities_at(target_x, target_y)
        entities_at_feet = self.game_map.get_entities_at(int(self.party.x), int(self.party.y))

        entity_to_interact = None
        for entity in entities_in_front:
            if isinstance(entity, (Chest, ItemPile)):
                entity_to_interact = entity
                break
        
        if not entity_to_interact:
            for entity in entities_at_feet:
                if isinstance(entity, (Chest, ItemPile)):
                    entity_to_interact = entity
                    break
        
        if entity_to_interact:
            if isinstance(entity_to_interact, Chest):
                if action == "Open":
                    items = entity_to_interact.interact(self.party)
                    if isinstance(items, list):
                        new_state = LootState(self.game, self.party, entity_to_interact)
                        self.game.push_state(new_state)
                    else:
                        self.game_gui.add_message(items)
                elif action == "Inspect":
                    message = entity_to_interact.inspect(self.party)
                    self.game_gui.add_message(message)
                elif action == "Disarm":
                    message = entity_to_interact.disarm(self.party)
                    self.game_gui.add_message(message)
            elif isinstance(entity_to_interact, ItemPile):
                if action == "Loot":
                    items = entity_to_interact.interact(self.party)
                    new_state = LootState(self.game, self.party, entity_to_interact)
                    self.game.push_state(new_state)

    def draw(self, surface, clock):
        if not self.minimap_ui.visible:
            self.raycaster.cast_rays(surface)
        
        if self.game.show_fps:
            self.game_gui.update_fps(clock.get_fps())
        
        self.minimap_ui.draw(surface, self.game_map, self.party)
        self.game_gui.update_message_log()
        self.game_gui.update_compass(self.party.facing)
        self.game_gui.draw_minimap(surface, self.game_map, self.party)
        self.game_gui.update_party_stats(self.party)
        pass