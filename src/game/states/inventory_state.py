import pygame
from pygame.locals import K_i, K_ESCAPE

from .base_state import BaseState
from ui.inventory_ui import InventoryUI
from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class InventoryState(BaseState):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.inventory_ui = InventoryUI(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.inventory_ui.toggle_visibility() # Should be visible when state is active
        self.messages = []

    def get_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == K_i or event.key == K_ESCAPE:
                self.done = True  # Signal to pop this state
            else:
                item = self.inventory_ui.handle_input(event, self.player)
                if item:
                    # For now, use the item on the first character
                    if self.player.characters:
                        character = self.player.characters[0]
                        result = item.use(character)
                        self.player.remove_from_inventory(item)
                        self.messages.append(result)
                    else:
                        self.messages.append("No characters in the party to use the item on.")

    def draw(self, surface, clock):
        self.inventory_ui.draw(surface, self.player)