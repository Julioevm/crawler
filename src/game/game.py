import pygame
import sys
from config.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from game.states.playing_state import PlayingState

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
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        self.cleanup()

    def handle_events(self):
        """
        Handles global events and passes events to the current state.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            if self.states:
                self.states[-1].get_event(event)

    def update(self, dt):
        """
        Updates the current game state.
        """
        if self.states:
            self.states[-1].update(dt)
            if self.states[-1].quit:
                self.running = False
            elif self.states[-1].done:
                self.pop_state()
                if self.states:
                    self.states[-1].startup(self.states[-1].persist)


    def draw(self):
        """
        Draws the screen based on the current game state.
        """
        self.screen.fill((0, 0, 0))
        for state in self.states:
            state.draw(self.screen, self.clock)
        pygame.display.flip()

    def cleanup(self):
        """
        Cleans up resources before exiting the game.
        """
        pygame.quit()
        sys.exit()
