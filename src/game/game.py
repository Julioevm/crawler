import pygame
import sys
from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from game.states.playing_state import PlayingState
from ui.game_gui import GameGUI
from engine.texture_manager import TextureManager

class Game:
    """
    The main Game class.

    This class initializes the game, runs the main game loop, and manages game states.
    """
    def __init__(self, show_fps=False):
        """
        Initializes the game, including pygame, the screen, and the clock.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Crawler - First-Person Dungeon Crawler")
        self.clock = pygame.time.Clock()
        self.running = True
        self.states = []
        self.show_fps = show_fps

        self.texture_manager = TextureManager()
        self.game_gui = GameGUI(self.texture_manager, self.show_fps)

        self.load_states()

    def load_states(self):
        self.playing_state = PlayingState(self)
        self.states.append(self.playing_state)

    def push_state(self, state):
        self.states.append(state)

    def pop_state(self):
        self.states.pop()

    def run(self):
        """
        The main game loop.
        """
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(time_delta)
            self.draw()

        self.cleanup()

    def handle_events(self):
        """
        Handles global events and passes events to the current state.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Pass events to the GUI manager
            self.game_gui.process_events(event)

            if self.states:
                action = self.states[-1].get_event(event)
                if action:
                    # If the state returns an action, handle it
                    # This part might need more logic later
                    pass

    def update(self, time_delta):
        """
        Updates the current game state.
        """
        if self.states:
            self.states[-1].update(time_delta)
            if self.states[-1].quit:
                self.running = False
            elif self.states[-1].done:
                self.pop_state()
        
        self.game_gui.update(time_delta)


    def draw(self):
        """
        Draws the screen based on the current game state.
        """
        self.screen.fill((0, 0, 0))
        if self.states:
            self.states[-1].draw(self.screen, self.clock)
        
        self.game_gui.draw(self.screen)
        self.game_gui.combat_ui.draw(self.screen)
        pygame.display.flip()

    def cleanup(self):
        """
        Cleans up resources before exiting the game.
        """
        pygame.quit()
        sys.exit()
