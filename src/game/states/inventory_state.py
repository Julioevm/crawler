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
                inventory_result = self.inventory_ui.handle_input(event, self.player)
                if inventory_result:
                    self.messages.append(inventory_result)

    def draw(self, screen, clock):
        self.inventory_ui.draw(screen, self.player)