import pygame
from .base_state import BaseState
from ui.combat_ui import CombatUI
from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class CombatState(BaseState):
    def __init__(self, game, party, enemy, combat_manager):
        super().__init__()
        self.game = game
        self.party = party
        self.enemy = enemy
        self.combat_manager = combat_manager
        self.combat_ui = CombatUI(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        combat_log = self.combat_manager.start_combat(self.party, self.enemy)
        self.combat_ui.start_combat(self.party, self.enemy)
        # TODO: Pass combat log to a message system

    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            combat_result = self.combat_ui.handle_input(event, self.combat_manager)
            if combat_result:
                if combat_result == "victory":
                    # TODO: Pass message to a message system
                    if self.enemy in self.game.playing_state.game_map.entities:
                        self.game.playing_state.game_map.remove_entity(self.enemy)
                elif combat_result == "defeat":
                    # TODO: Pass message to a message system
                    self.quit = True
                elif combat_result == "fled":
                    # TODO: Pass message to a message system
                    pass
                self.done = True # End combat

    def draw(self, screen, clock):
        # Draw the underlying playing state
        self.game.playing_state.draw(screen, clock)
        # Draw the combat UI over it
        self.combat_ui.draw(screen, self.combat_manager)