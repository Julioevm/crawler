import pygame
import os
import random

# Initialize pygame
pygame.init()

# Create assets directories if they don't exist
os.makedirs("assets/textures", exist_ok=True)

# Create a better dungeon wall texture with more detail
surface = pygame.Surface((64, 128))  # Taller texture for better scaling

# Base stone color
base_color = (100, 100, 110)
surface.fill(base_color)

# Add some variation to simulate stone texture
for _ in range(100):
    x = random.randint(0, 63)
    y = random.randint(0, 127)
    size = random.randint(1, 4)
    darkness = random.randint(10, 30)
    color = (base_color[0] - darkness, base_color[1] - darkness, base_color[2] - darkness)
    pygame.draw.rect(surface, color, (x, y, size, size))

# Add some lighter spots to simulate wear
for _ in range(30):
    x = random.randint(0, 63)
    y = random.randint(0, 127)
    size = random.randint(1, 3)
    brightness = random.randint(10, 20)
    color = (base_color[0] + brightness, base_color[1] + brightness, base_color[2] + brightness)
    pygame.draw.rect(surface, color, (x, y, size, size))

# Add some vertical lines to simulate mortar between stones
for x in range(0, 64, 8):
    pygame.draw.line(surface, (80, 80, 90), (x, 0), (x, 127), 1)

pygame.image.save(surface, "assets/textures/dungeon_wall.png")

print("Improved dungeon wall texture created!")