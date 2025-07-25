#!/usr/bin/env python3
"""
Main entry point for the Crawler game.
"""

from game.game import Game

def main():
    """
    Initializes and runs the game.
    """
    game = Game()
    game.run()

if __name__ == "__main__":
    main()