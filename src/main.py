#!/usr/bin/env python3
"""
Main entry point for the Crawler game.
"""

import argparse
from game.game import Game

def main():
    """
    Initializes and runs the game.
    """
    parser = argparse.ArgumentParser(description="Crawler - First-Person Dungeon Crawler")
    parser.add_argument("--fps", action="store_true", help="Show FPS counter")
    args = parser.parse_args()

    game = Game(show_fps=args.fps)
    game.run()

if __name__ == "__main__":
    main()