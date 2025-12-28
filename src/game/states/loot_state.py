"""
Loot state for when the player is looting a chest or item pile.
"""

import pygame
from pygame.locals import K_ESCAPE

from .base_state import BaseState
from ui.loot_ui import LootUI
from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class LootState(BaseState):
    def __init__(self, game, party, container):
        super().__init__()
        self.game = game
        self.party = party
        self.container = container
        self.loot_ui = LootUI(SCREEN_WIDTH, SCREEN_HEIGHT, container)
        self.loot_ui.toggle_visibility()

    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                self.done = True
            else:
                result = self.loot_ui.handle_input(event)
                if result:
                    if "take" in result:
                        item = result["take"]
                        self.party.add_to_inventory(item)
                        self.container.remove_item(item)
                        if not self.container.items:
                            self.game.playing_state.game_map.remove_entity(self.container)
                            self.done = True
                    elif "take_all" in result:
                        for item in self.container.items:
                            self.party.add_to_inventory(item)
                        self.container.items = []
                        self.game.playing_state.game_map.remove_entity(self.container)
                        self.done = True

    def draw(self, surface, clock):
        self.loot_ui.draw(surface)