class BaseState:
    """
    A base class for all game states.
    """
    def __init__(self):
        self.done = False
        self.quit = False
        self.next_state = None
        self.screen_rect = None

    def startup(self, persistent):
        """
        Called when a state resumes being active.
        Allows passing of data between states.
        """
        self.persist = persistent

    def get_event(self, event):
        """
        Handle a single event.
        """
        pass

    def update(self, dt):
        """
        Update the state.
        dt is the time since last update.
        """
        pass

    def draw(self, surface, clock):
        """
        Draw the state to the surface.
        """
        pass