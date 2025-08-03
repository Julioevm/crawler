import pygame
import pygame_gui
import os

from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from .particle_system import ParticleManager

class CombatUI:
    """UI for displaying and managing combat."""
    
    def __init__(self, manager, texture_manager):
        self.manager = manager
        self.texture_manager = texture_manager
        self.particle_manager = ParticleManager()
        self.font = pygame.font.Font(None, 24) # For damage text
        self.visible = False
        self.selected_target = 0
        self.actions = ["Attack (A)", "Spell (S)", "Item (I)", "Guard (G)", "Flee (F)"]
        self.action_buttons = []
        self.enemy_elements = []

    def start_combat(self, party, enemies):
        """Start combat display."""
        self.visible = True
        self.selected_action = 0
        self.selected_target = 0
        self.party = party
        self.enemies = enemies

    def end_combat(self):
        """End combat display."""
        self.visible = False
        self.party = None
        self.enemies = []
        self.particle_manager.clear()
        if hasattr(self, 'action_panel'):
            self.action_panel.hide()
            for elem in self.enemy_elements:
                elem["panel"].hide()

    def handle_event(self, event):
        """Handle input events for combat."""
        if not self.visible:
            return None

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for i, button in enumerate(self.action_buttons):
                if event.ui_element == button:
                    action = self.actions[i].split(" ")[0].lower()
                    if action == "attack":
                        if self.enemies:
                            target = self.enemies[self.selected_target]
                            return {"action": "attack", "target": target}
                    # Other actions will be implemented later
                    else:
                        return {"action": action}

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                return {"action": "attack", "target": self.enemies[self.selected_target]}
            elif event.key == pygame.K_s:
                return {"action": "spell"}
            elif event.key == pygame.K_i:
                return {"action": "item"}
            elif event.key == pygame.K_g:
                return {"action": "guard"}
            elif event.key == pygame.K_f:
                return {"action": "flee"}
            elif event.key == pygame.K_LEFT:
                self.selected_target = max(0, self.selected_target - 1)
                self.update_target_selection()
            elif event.key == pygame.K_RIGHT:
                self.selected_target = min(len(self.enemies) - 1, self.selected_target + 1)
                self.update_target_selection()

        return None

    def build(self):
        """Build the combat UI elements."""
        if hasattr(self, 'action_panel'):
            self.action_panel.kill()
        self.action_buttons = []
        
        panel_width = 600
        panel_height = 60
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = SCREEN_HEIGHT - 150 - panel_height - 10 # Above party panel

        self.action_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((panel_x, panel_y), (panel_width, panel_height)),
            manager=self.manager,
            object_id="#action_button_container"
        )

        button_width, button_height = 100, 40
        spacing = 20
        start_x = (panel_width - (len(self.actions) * button_width + (len(self.actions) - 1) * spacing)) // 2
        
        for i, action in enumerate(self.actions):
            button_x = start_x + i * (button_width + spacing)
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((button_x, 10), (button_width, button_height)),
                text=action,
                manager=self.manager,
                container=self.action_panel
            )
            self.action_buttons.append(button)

        self.build_enemy_display()
        self.hide()

    def build_enemy_display(self):
        """Create UI elements for each enemy."""
        # Clear existing enemy elements
        for elem in self.enemy_elements:
            elem["panel"].kill()
        self.enemy_elements = []

        num_enemies = len(self.enemies)
        
        # Define layout properties
        front_row_y = 200
        back_row_y = 100
        row_x_start = (SCREEN_WIDTH - 3 * 120) // 2  # Centered layout
        
        front_row_size = (100, 120)
        back_row_size = (80, 100)

        for i, enemy in enumerate(self.enemies):
            if i < 3:  # Front row
                row = 0
                col = i
                x_pos = row_x_start + col * 120
                y_pos = front_row_y
                size = front_row_size
            else:  # Back row
                row = 1
                col = i - 3
                x_pos = row_x_start + col * 120 + 20 # Offset for perspective
                y_pos = back_row_y
                size = back_row_size

            panel = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect((x_pos, y_pos), size),
                manager=self.manager,
                object_id="#enemy_container"
            )

            sprite_name = os.path.splitext(enemy.sprite)[0]
            sprite_surface = self.texture_manager.get_sprite(sprite_name)
            if sprite_surface is None:
                sprite_path = os.path.join(self.texture_manager.assets_path, "sprites", enemy.sprite)
                sprite_surface = self.texture_manager.load_sprite(sprite_name, sprite_path)

            sprite = pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect((0, 0), (size[0], size[1] - 20)),
                image_surface=sprite_surface,
                manager=self.manager,
                container=panel
            )

            hp_bar = pygame_gui.elements.UIStatusBar(
                relative_rect=pygame.Rect((5, size[1] - 20), (size[0] - 10, 15)),
                manager=self.manager,
                container=panel
            )
            hp_bar.percent_full = (enemy.hp / enemy.max_hp) * 100

            self.enemy_elements.append({"panel": panel, "sprite": sprite, "hp_bar": hp_bar})
        
        self.update_target_selection()

    def update_target_selection(self):
        """Highlight the selected enemy."""
        for i, elem in enumerate(self.enemy_elements):
            if i == self.selected_target:
                # Create a temporary highlight by changing the sprite's blend mode
                elem["sprite"].image.set_colorkey((255,0,255))
                elem["sprite"].image.set_alpha(200)
            else:
                elem["sprite"].image.set_colorkey(None)
                elem["sprite"].image.set_alpha(255)
            elem["sprite"].rebuild()

    def show(self):
        """Show the combat UI."""
        self.visible = True
        self.action_panel.show()
        for elem in self.enemy_elements:
            elem["panel"].show()

    def hide(self):
        """Hide the combat UI."""
        self.visible = False
        if hasattr(self, 'action_panel'):
            self.action_panel.hide()
            for elem in self.enemy_elements:
                elem["panel"].hide()

    def show_damage(self, target_index, damage, is_enemy=True):
        """Display damage numbers and effects on a target."""
        if is_enemy:
            if target_index < len(self.enemy_elements):
                panel_rect = self.enemy_elements[target_index]["panel"].get_abs_rect()
                x = panel_rect.centerx
                y = panel_rect.centery
                self.particle_manager.create_damage_text(x, y, str(damage), self.font)
                self.particle_manager.create_blood_splatter(x, y)
        else:
            # This will be called from GameGUI, which has access to party frames
            pass

    def draw(self, surface):
        """Draw additional UI elements, like particles."""
        if self.visible:
            self.particle_manager.draw(surface)

    def update(self, time_delta):
        """Update combat UI elements."""
        if not self.visible:
            return
        
        self.particle_manager.update()

        for i, enemy in enumerate(self.enemies):
            if i < len(self.enemy_elements):
                self.enemy_elements[i]["hp_bar"].percent_full = (enemy.hp / enemy.max_hp) * 100