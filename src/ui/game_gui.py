import pygame
import pygame_gui
import os

from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from ui.combat_ui import CombatUI
from entities.chest import Chest
from entities.item_pile import ItemPile

class GameGUI:
    """Manages the game's GUI using pygame-gui."""

    CHAR_PANEL_WIDTH = 150
    CHAR_PANEL_HEIGHT = 140

    def __init__(self, texture_manager, show_fps=False):
        self.manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT),
                                            "data/themes/game_gui.json",
                                            enable_live_theme_updates=False)
        
        self.manager.add_font_paths("morris_roman_black_font",
                                    "assets/fonts/MorrisRoman-Black.ttf")

        self.texture_manager = texture_manager
        self.combat_ui = CombatUI(self.manager, self.texture_manager)
        self.messages = []
        self._last_messages = []  # Track last messages to avoid unnecessary updates

        if show_fps:
            self.fps_label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 50, 0), (100, 30)),
                text="FPS: 0",
                manager=self.manager,
                object_id="#fps_label"
            )
        else:
            self.fps_label = None

        # Message Log Panel
        self.message_log_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((10, 10), (400, 150)),
            manager=self.manager,
            object_id="#message_log_panel"
        )

        self.message_log = pygame_gui.elements.UITextBox(
            html_text="",
            relative_rect=pygame.Rect((5, 5), (370, 120)),
            manager=self.manager,
            container=self.message_log_panel,
            object_id="#message_log"
        )
        self.message_log_collapse_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((360, -5), (30, 20)), text='-', manager=self.manager, container=self.message_log_panel)
        self.message_log_collapsed = False

        # Minimap Panel
        self.minimap_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((SCREEN_WIDTH - 210, 10), (200, 200)),
            manager=self.manager,
            object_id="#minimap_panel"
        )

        self.compass_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 160), (180, 20)),
            text="- N -",
            manager=self.manager,
            container=self.minimap_panel,
            object_id="#compass_label"
        )
        self.minimap_collapse_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((160, -5), (30, 20)), text='-', manager=self.manager, container=self.minimap_panel)
        self.minimap_collapsed = False

        # Party Stats Panel
        self.party_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, SCREEN_HEIGHT - 150), (SCREEN_WIDTH, 150)),
            manager=self.manager,
            object_id="#party_panel"
        )
        self.party_collapse_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((SCREEN_WIDTH - 40, -5), (30, 20)), text='-', manager=self.manager, container=self.party_panel)
        self.party_collapsed = False
        self.character_elements = []

        # Interaction Panel
        self.interaction_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 200), (300, 50)),
            manager=self.manager,
            object_id="#interaction_panel",
            visible=False
        )
        self.interaction_buttons = []

    def process_events(self, event):
        """Process GUI events."""
        self.manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.message_log_collapse_button:
                self.toggle_message_log()
            elif event.ui_element == self.minimap_collapse_button:
                self.toggle_minimap()
            elif event.ui_element == self.party_collapse_button:
                self.toggle_party_stats()
            else:
                for button in self.interaction_buttons:
                    if event.ui_element == button:
                        return {"interaction": button.text}
            
            # Forward events to combat UI if it's visible
            if self.combat_ui.visible:
                return self.combat_ui.handle_event(event)
            return None

    def update(self, time_delta):
        """Update the GUI."""
        self.manager.update(time_delta)
        if self.combat_ui.visible:
            self.combat_ui.update(time_delta)

    def draw(self, screen):
        """Draw the GUI."""
        self.manager.draw_ui(screen)

    def add_message(self, message):
        """Add a message to the log."""
        self.messages.append(message)
        # Keep the log from getting too long
        if len(self.messages) > 100:
            self.messages.pop(0)
        self.update_message_log()

    def update_message_log(self):
        """Update the message log with new messages."""
        # Only update if messages have changed to preserve scroll position
        if self.messages != self._last_messages:
            # The log shows the most recent messages first, so we reverse the list
            # and join them with line breaks.
            formatted_messages = "<br>".join(reversed(self.messages))
            self.message_log.set_text(formatted_messages)
            self._last_messages = self.messages.copy()  # Store a copy to track changes

    def update_compass(self, facing):
        """Update the compass direction."""
        directions = ["N", "E", "S", "W"]
        self.compass_label.set_text(f"- {directions[facing]} -")

    def update_fps(self, fps):
        """Update the FPS counter."""
        if self.fps_label:
            self.fps_label.set_text(f"FPS: {int(fps)}")

    def draw_minimap(self, surface, game_map, party):
        """Draw the minimap on the specified surface."""
        # Don't draw the minimap if it's collapsed
        if self.minimap_collapsed:
            return

        map_surface = self.minimap_panel.image
        
        # Don't fill the entire surface - let the panel's themed background and border show
        # Only fill the inner area where we'll draw the map
        border_width = 4  # Account for the panel's border and padding
        inner_rect = pygame.Rect(border_width, border_width,
                                map_surface.get_width() - (border_width * 2),
                                map_surface.get_height() - 40 - (border_width * 2))  # leave space for compass
        pygame.draw.rect(map_surface, (15, 15, 15), inner_rect)  # Dark background for map area

        cell_size = 10
        map_width = inner_rect.width
        map_height = inner_rect.height

        # Center the map view on the player
        start_x = max(0, party.x - (map_width // (2 * cell_size)))
        start_y = max(0, party.y - (map_height // (2 * cell_size)))
        end_x = start_x + (map_width // cell_size)
        end_y = start_y + (map_height // cell_size)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if 0 <= x < game_map.width and 0 <= y < game_map.height:
                    screen_x = inner_rect.x + (x - start_x) * cell_size
                    screen_y = inner_rect.y + (y - start_y) * cell_size
                    if game_map.tiles[y][x] == 1:
                        pygame.draw.rect(map_surface, (100, 100, 100), (screen_x, screen_y, cell_size, cell_size))
                    else:
                        pygame.draw.rect(map_surface, (50, 50, 50), (screen_x, screen_y, cell_size, cell_size))

        # Draw player position
        player_screen_x = inner_rect.x + (party.x - start_x) * cell_size
        player_screen_y = inner_rect.y + (party.y - start_y) * cell_size
        pygame.draw.rect(map_surface, (255, 0, 0), (player_screen_x, player_screen_y, cell_size, cell_size))

    def create_party_frames(self, party):
        """Create the UI elements for each character in the party."""
        self.character_elements = []
        spacing = 10
        start_x = (SCREEN_WIDTH - (len(party.characters) * (self.CHAR_PANEL_WIDTH + spacing))) // 2

        for i, character in enumerate(party.characters):
            char_panel = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect((start_x + i * (self.CHAR_PANEL_WIDTH + spacing), 10),
                                          (self.CHAR_PANEL_WIDTH, self.CHAR_PANEL_HEIGHT)),
                manager=self.manager,
                container=self.party_panel,
                object_id="@char_panel"
            )

            portrait_surface = pygame.Surface((64, 64), pygame.SRCALPHA)
            if character.portrait:
                portrait_path = os.path.join(self.texture_manager.assets_path, "portraits", character.portrait)
                portrait_image = self.texture_manager.load_portrait(character.portrait, portrait_path)
                if portrait_image:
                    portrait_surface = portrait_image

            portrait = pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect((15, 10), (64, 64)),
                image_surface=portrait_surface,
                manager=self.manager,
                container=char_panel
            )

            name = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((15, 80), (120, 20)),
                text=character.name,
                manager=self.manager,
                container=char_panel,
                object_id="@name_label"
            )

            bar_width = 110

            hp_bar = pygame_gui.elements.UIStatusBar(
                relative_rect=pygame.Rect((15, 100), (bar_width, 10)),
                manager=self.manager,
                container=char_panel
            )
            hp_bar.percent_full = (character.hp / character.max_hp) * 100

            mp_bar = pygame_gui.elements.UIStatusBar(
                relative_rect=pygame.Rect((15, 112), (bar_width, 10)),
                manager=self.manager,
                container=char_panel,
                object_id="@mp_bar"
            )
            mp_bar.percent_full = (character.mp / character.max_mp) * 100 if character.max_mp > 0 else 0

            self.character_elements.append({
                "panel": char_panel,
                "portrait": portrait,
                "name": name,
                "hp_bar": hp_bar,
                "mp_bar": mp_bar
            })

    def update_party_stats(self, party):
        """Update the stats for each character in the party."""
        if not self.character_elements:
             self.create_party_frames(party)

        for i, character in enumerate(party.characters):
            if i < len(self.character_elements):
                elements = self.character_elements[i]
                elements["hp_bar"].percent_full = (character.hp / character.max_hp) * 100
                elements["mp_bar"].percent_full = (character.mp / character.max_mp) * 100 if character.max_mp > 0 else 0

    def show_damage_on_party_member(self, character_index, damage):
        """Display damage on a party member's portrait."""
        if character_index < len(self.character_elements):
            elements = self.character_elements[character_index]
            portrait_rect = elements["portrait"].get_abs_rect()
            x = portrait_rect.centerx
            y = portrait_rect.centery
            self.combat_ui.particle_manager.create_damage_text(x, y, str(damage), self.combat_ui.font)
            self.combat_ui.particle_manager.create_blood_splatter(x, y)

    def show_interaction_buttons(self, entity):
        """Show interaction buttons for a given entity."""
        self.hide_interaction_buttons()
        self.interaction_panel.show()
        
        actions = []
        if isinstance(entity, Chest):
            actions = ["Open", "Inspect", "Disarm"]
        elif isinstance(entity, ItemPile):
            actions = ["Loot"]

        button_width = 80
        spacing = 10
        start_x = (300 - (len(actions) * (button_width + spacing))) // 2

        for i, action in enumerate(actions):
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((start_x + i * (button_width + spacing), 5), (button_width, 30)),
                text=action,
                manager=self.manager,
                container=self.interaction_panel
            )
            self.interaction_buttons.append(button)

    def hide_interaction_buttons(self):
        """Hide all interaction buttons."""
        for button in self.interaction_buttons:
            button.kill()
        self.interaction_buttons = []
        self.interaction_panel.hide()

    def toggle_message_log(self):
        """Toggle the visibility of the message log."""
        self.message_log_collapsed = not self.message_log_collapsed
        if self.message_log_collapsed:
            self.message_log_panel.set_dimensions((400, 60))
            self.message_log.set_dimensions((370, 35))
            self.message_log.scroll_bar_width = 0
            self.message_log.rebuild()
            self.message_log_collapse_button.set_text('+')
        else:
            self.message_log_panel.set_dimensions((400, 150))
            self.message_log.set_dimensions((370, 120))
            self.message_log.scroll_bar_width = 20
            self.message_log.rebuild()
            self.message_log_collapse_button.set_text('-')

    def toggle_minimap(self):
        """Toggle the visibility of the minimap."""
        self.minimap_collapsed = not self.minimap_collapsed
        if self.minimap_collapsed:
            self.minimap_panel.set_dimensions((200, 60))
            # Move compass to be visible in collapsed state
            self.compass_label.set_relative_position((10, 20))
            self.minimap_collapse_button.set_text('+')
        else:
            self.minimap_panel.set_dimensions((200, 200))
            # Move compass back to original position
            self.compass_label.set_relative_position((0, 160))
            self.minimap_collapse_button.set_text('-')

    def toggle_party_stats(self):
        """Toggle the visibility of the party stats."""
        self.party_collapsed = not self.party_collapsed
        if self.party_collapsed:
            self.party_panel.set_dimensions((SCREEN_WIDTH, 80))
            self.party_panel.set_relative_position((0, SCREEN_HEIGHT - 80))
            for elements in self.character_elements:
                elements["portrait"].hide()
                elements["panel"].set_dimensions((self.CHAR_PANEL_WIDTH, 70))
                elements["name"].set_relative_position((10, 5))
                elements["hp_bar"].set_relative_position((10, 25))
                elements["mp_bar"].set_relative_position((10, 37))
            self.party_collapse_button.set_text('+')
        else:
            self.party_panel.set_dimensions((SCREEN_WIDTH, 150))
            self.party_panel.set_relative_position((0, SCREEN_HEIGHT - 150))
            for elements in self.character_elements:
                elements["portrait"].show()
                elements["panel"].set_dimensions((self.CHAR_PANEL_WIDTH, self.CHAR_PANEL_HEIGHT))
                elements["name"].set_relative_position((10, 80))
                elements["hp_bar"].set_relative_position((10, 100))
                elements["mp_bar"].set_relative_position((10, 112))
            self.party_collapse_button.set_text('-')
